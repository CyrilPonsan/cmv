from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt

from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..settings.models import User
from ..settings.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

redis = redis_client
logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_session(user_id: str):
    session_id = str(uuid.uuid4())
    redis.setex(f"session:{session_id}", 3600, user_id)  # expire après 1 heure
    return session_id


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        session_id: str = payload.get("session_id")
        if session_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Vérifier si la session est toujours valide dans Redis
    if not redis.exists(f"session:{session_id}"):
        raise credentials_exception

    # Ici, vous récupéreriez les détails de l'utilisateur depuis votre base de données
    user = get_user(user_id)  # Fonction à implémenter
    if user is None:
        raise credentials_exception
    return user
