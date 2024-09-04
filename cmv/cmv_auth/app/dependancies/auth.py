from datetime import datetime, timedelta
import uuid
from typing import Optional

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..settings.models import User
from ..schemas.user import User as CurrentUser
from ..settings.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from .db_session import get_db

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


def get_user_with_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password) or not user.is_active:
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_session(user_id: str):
    session_id = str(uuid.uuid4())
    redis.setex(f"session:{session_id}", 3600, user_id)  # expire après 1 heure
    return session_id


def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_current_user(
    db=Depends(get_db), token: str = Depends(get_token_from_cookie)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
        session_id: str = payload.get("session_id")
        if not session_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Vérifier si la session est toujours valide dans Redis
    if not redis_client.exists(f"session:{session_id}"):
        raise credentials_exception

    user = get_user_with_id(
        db, user_id
    )  # Implémentez cette fonction pour récupérer l'utilisateur
    if user is None:
        raise credentials_exception
    return user
