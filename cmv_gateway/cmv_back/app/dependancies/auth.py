# Imports des modules standards Python
from datetime import datetime, timedelta
import uuid
from typing import Optional, Annotated

# Imports des dépendances FastAPI et autres frameworks
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError

# Imports des modules internes de l'application
from app.repositories.permissions_crud import PermissionRepository
from app.repositories.user_crud import PgUserRepository
from app.schemas.user import User
from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM
from .db_session import get_db

# Initialisation des clients Redis et du logger
redis = redis_client
logger = LoggerSetup()


# Configuration de l'authentification OAuth2 pour la gestion des tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration du hachage des mots de passe avec bcrypt
# Permet de sécuriser le stockage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Liste des endpoints qui ne nécessitent pas d'authentification complète
# Ces endpoints sont accessibles avec une authentification basique
basic_authorizations = [
    "/api/auth/users/me",
]

# Exceptions personnalisées pour la gestion des erreurs d'authentification
# Utilisées pour retourner des réponses HTTP appropriées en cas d'erreur
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

not_authenticated_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="not_authenticated",
)


def verify_password(plain_password, hashed_password):
    """
    Vérifie si le mot de passe en clair correspond au hash stocké
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe stocké
    Returns:
        bool: True si les mots de passe correspondent, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    db: Session, username: str, password: str, request: Request
) -> User:
    """
    Authentifie un utilisateur à partir de ses identifiants
    Args:
        db: Session de base de données
        username: Nom d'utilisateur
        password: Mot de passe
        request: Requête HTTP
    Returns:
        User: Utilisateur authentifié
    Raises:
        HTTPException: Si l'authentification échoue
    """
    user = await PgUserRepository.get_user(db, username)
    if not user:
        logger.write_log(
            f"Failed connection attempt using : {username}", request=request
        )
        raise credentials_exception
    if not verify_password(password, user.password) or not user.is_active:
        logger.write_log(
            f"Failed connection attempt from : {user.id_user}", request=request
        )
        raise credentials_exception
    return user


async def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crée un token JWT avec les données fournies et une durée de validité
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token
    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY or "", algorithm=ALGORITHM or "")
    return encoded_jwt


async def create_session(user_id: str):
    """
    Crée une session dans Redis avec un UUID unique
    Args:
        user_id: Identifiant de l'utilisateur
    Returns:
        str: Identifiant de session
    """
    session_id = str(uuid.uuid4())
    await redis.setex(f"session:{session_id}", 3600, user_id)  # expire après 1 heure
    return session_id


def get_token_from_cookie(request: Request):
    """
    Récupère le token d'accès depuis les cookies de la requête
    Args:
        request: Requête HTTP
    Returns:
        str: Token d'accès
    Raises:
        HTTPException: Si le token n'est pas trouvé
    """
    token = request.cookies.get("access_token")
    if not token:
        raise not_authenticated_exception
    return token


async def get_current_user(
    db=Depends(get_db), token: str = Depends(get_token_from_cookie)
):
    """
    Récupère l'utilisateur courant à partir du token d'accès
    Args:
        db: Session de base de données
        token: Token d'accès
    Returns:
        User: Utilisateur courant
    Raises:
        HTTPException: Si l'authentification échoue
    """
    try:
        if not token:
            print("#### no token ####")
            raise not_authenticated_exception
        # vérifie que le token ne soit pas blacklist
        is_blacklisted = await redis_client.get(f"blacklist:{token}")
        if is_blacklisted:
            raise not_authenticated_exception
        payload = jwt.decode(token, SECRET_KEY or "", algorithms=[ALGORITHM or ""])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exception
        session_id: str | None = payload.get("session_id")
        if not session_id:
            raise not_authenticated_exception
    except JWTError:
        raise not_authenticated_exception

    # Vérifier si la session est toujours valide dans Redis
    session_exists = await redis_client.exists(f"session:{session_id}")
    if not session_exists:
        raise not_authenticated_exception
    user = await PgUserRepository.get_user_with_id(db, user_id)
    if user is None or user.is_active is False:
        raise credentials_exception
    return user


def get_dynamic_permissions(action: str, resource: str) -> str:
    """
    Génère une fonction de vérification des permissions dynamique
    Args:
        action: Action à vérifier
        resource: Ressource concernée
    Returns:
        Callable: Fonction de vérification des permissions
    """

    async def get_permissions(
        current_user: Annotated[User, Depends(get_current_user)],
        db=Depends(get_db),
    ) -> str:
        if not await check_permissions(db, current_user.role.name, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="not_authorized"
            )
        internal_payload = {
            "user_id": current_user.id_user,
            "role": current_user.role.name,
            "exp": datetime.now() + timedelta(seconds=15),  # Durée de vie courte
            "source": "api_gateway",
        }
        return jwt.encode(internal_payload, SECRET_KEY or "", algorithm=ALGORITHM or "")

    return get_permissions


async def check_permissions(
    db: Session,
    role: str,
    action: str,
    resource: str,
) -> bool:
    """
    Vérifie les permissions d'un rôle pour une action sur une ressource
    Args:
        db: Session de base de données
        role: Rôle à vérifier
        action: Action à vérifier
        resource: Ressource concernée
    Returns:
        bool: True si autorisé, False sinon
    Raises:
        HTTPException: Si non autorisé
    """
    authorized = await PermissionRepository.check_permission(db, role, action, resource)
    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette ressource.",
        )
    return True
