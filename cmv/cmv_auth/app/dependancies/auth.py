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
def create_or_renew_session(user_id: int):
    session_id = secrets.token_urlsafe(32)
    session_key = f"session:{session_id}"

    # Stocker la session dans Redis avec une expiration de 1 heure
    redis_client.hmset(session_key, {"user_id": user_id})
    redis_client.expire(session_key, timedelta(hours=1))

    return session_id


# Dépendance pour vérifier la session
async def get_current_user(request: Request, db=Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session non valide ou expirée.",
        )

    session_key = f"session:{session_id}"

    # Utiliser await pour récupérer les données de la session
    session_data = await redis_client.hgetall(session_key)

    # Convertir les données de session de bytes en str
    session_data = {
        k.decode("utf-8"): v.decode("utf-8") for k, v in session_data.items()
    }

    # Vérification si session_data est vide ou ne contient pas le user_id
    if not session_data or "user_id" not in session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session non valide ou expirée.",
        )

    user_id = session_data.get("user_id")

    # Récupérer l'utilisateur à partir de la base de données
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif ou non trouvé.",
        )

    # Renouveler l'expiration de la session
    await redis_client.expire(session_key, timedelta(hours=1))

    # Vérification des autorisations
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
