from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM

redis = redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_authorizations = [
    "/api/auth/users/me",
]


def check_authorization(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:

    payload: dict = jwt.decode(token, SECRET_KEY or "", algorithms=[ALGORITHM])
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not_authorized"
        )
    return payload
