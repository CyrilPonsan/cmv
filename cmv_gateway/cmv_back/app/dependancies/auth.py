from datetime import datetime, timedelta
import uuid
from typing import Optional, Annotated

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.repositories.permissions_crud import PgPermissionRepository
from app.repositories.user_crud import PgUserRepository
from app.schemas.user import User
from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM
from .db_session import get_db

redis = redis_client
logger = LoggerSetup()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_authorizations = [
    "/api/auth/users/me",
]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Adresse email ou mot de passe incorrect",
    headers={"WWW-Authenticate": "Bearer"},
)

not_authenticated_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="not_authenticated",
)


# Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    db: Session, username: str, password: str, request: Request
) -> User:
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


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_session(user_id: str):
    session_id = str(uuid.uuid4())
    await redis.setex(f"session:{session_id}", 3600, user_id)  # expire après 1 heure
    return session_id


def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise not_authenticated_exception
    return token


async def get_current_user(
    db=Depends(get_db), token: str = Depends(get_token_from_cookie)
):
    try:
        if not token:
            raise not_authenticated_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
        session_id: str = payload.get("session_id")
        if not session_id:
            raise not_authenticated_exception
    except JWTError:
        raise credentials_exception

    # Vérifier si la session est toujours valide dans Redis
    session_exists = await redis_client.exists(f"session:{session_id}")
    if not session_exists:
        raise not_authenticated_exception
    user = await PgUserRepository.get_user_with_id(db, user_id)
    if user is None or user.is_active is False:
        raise credentials_exception
    return user


def get_dynamic_permissions(action: str, resource: str) -> User:
    async def get_permissions(
        current_user: Annotated[User, Depends(get_current_user)],
        db=Depends(get_db),
    ):
        if await check_permissions(db, current_user.role.name, action, resource):
            return current_user

    return get_permissions


async def check_permissions(
    db: Session,
    role: str,
    action: str,
    resource: str,
) -> bool:
    authorized = await PgPermissionRepository.check_permission(
        db, role, action, resource
    )
    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette ressource.",
        )
    return True
