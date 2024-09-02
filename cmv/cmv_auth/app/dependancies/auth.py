from datetime import datetime, timedelta
import secrets
import redis
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
    session_data = {
        "user_id": str(user_id),
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
    }

    # Use hset to set multiple fields in the hash
    await redis_client.hset(session_key, mapping=session_data)

    # Set the expiration for the session
    await redis_client.expire(session_key, timedelta(hours=1))

    return session_id


# Dépendance pour vérifier la session
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session non valide ou expirée.",
        )

    session_key = f"session:{session_id}"
    session_data = await redis_client.hgetall(session_key)

    # Convert the session_data values to strings, if they are in bytes
    session_data = {
        k: v.decode("utf-8") if isinstance(v, bytes) else v
        for k, v in session_data.items()
    }

    # Verify if session_data contains the user_id
    if not session_data or "user_id" not in session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session non valide ou expirée.",
        )

    user_id = session_data["user_id"]

    # Further code to retrieve the user from the database, etc.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé.",
        )
    return user
