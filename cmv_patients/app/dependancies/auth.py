from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError


# from ..utils.logging_setup import LoggerSetup
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM
from .db_session import get_db

redis = redis_client
# logger_setup = LoggerSetup()
# LOGGER = logger_setup.write_log


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_authorizations = [
    "/api/auth/users/me",
]


def get_token_from_cookie(request: Request):
    print("Hello fonction")
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
    print(f"token : {token}")
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
    return True
