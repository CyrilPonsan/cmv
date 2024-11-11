from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM

redis = redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_authorization(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY or "", algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="not_authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the token",
        )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not_authorized"
        )

    return payload
