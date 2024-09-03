from datetime import timedelta
import secrets

from fastapi import HTTPException, status, Request, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..crud.auth_crud import check_permission
from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..settings.models import User
from .db_session import get_db

logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log

# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_authorizations = [
    "/api/auth/users/me",
]


# Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password) or not user.is_active:
        return False
    return user


# Fonction pour créer ou renouveler une session
async def create_or_renew_session(user_id: int):
    session_id = secrets.token_urlsafe(32)
    session_key = f"session:{session_id}"

    LOGGER(f"Création/renouvellement de session pour user_id: {user_id}", None)
    LOGGER(f"Clé de session: {session_key}", None)

    # Stocker la session dans Redis avec une expiration de 1 heure
    await redis_client.hmset(session_key, {"user_id": str(user_id)})
    await redis_client.expire(session_key, timedelta(hours=1))

    # Vérification immédiate
    session_data = await redis_client.hgetall(session_key)
    LOGGER(f"Données de session après création: {session_data}", None)

    return session_id


# Dépendance pour vérifier la session
async def get_current_user(request: Request, db=Depends(get_db)):
    session_id = request.cookies.get("session_id")
    LOGGER(f"Session ID récupéré : {session_id}", request)

    if not session_id:
        LOGGER("Aucun session_id trouvé dans les cookies", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="toto Session non valide ou expirée.",
        )

    session_key = f"session:{session_id}"
    LOGGER(f"Clé de session : {session_key}", request)

    # Récupération des données de session de Redis
    session_data = await redis_client.hgetall(session_key)
    LOGGER(f"Données de session récupérées : {session_data}", request)

    if not session_data:
        LOGGER("Aucune donnée de session trouvée dans Redis", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="tata Session non valide ou expirée. (Aucune donnée)",
        )

    if "user_id" not in session_data:
        LOGGER("user_id non trouvé dans les données de session", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="tata Session non valide ou expirée. (Pas de user_id)",
        )

    user_id = session_data.get("user_id")
    LOGGER(f"User ID récupéré : {user_id}", request)

    # Retrieve the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif ou non trouvé.",
        )

    # Renew the session expiration
    await redis_client.expire(session_key, timedelta(hours=1))

    # Check permissions
    resource = request.url.path.split("/")[3]
    authorization = check_permission(
        db=db,
        role=user.role.name,
        action=request.method.lower(),
        resource=resource,
    )

    if request.url.path not in basic_authorizations and not authorization:
        LOGGER(
            f"verboten to {request.method.lower()} on {resource} for {user.role.name}",
            request,
        )
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à effectuer cette action sur cette ressource.",
        )

    return user
