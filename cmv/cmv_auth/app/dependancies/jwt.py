from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..settings.config import SECRET_KEY, ALGORITHM
from app.dependancies.db_session import get_db
from app.schemas.user import User
from app.repositiries.user_crud import get_user_by_id
from ..crud.auth_crud import check_permission
from ..utils.logging_setup import LoggerSetup

logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

basic_authorizations = [
    "/api/auth/refresh",
    "/api/users/me",
]


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    current_time_utc = datetime.now(
        timezone.utc
    )  # Utilisation de l'heure actuelle en UTC
    if expires_delta:
        expire = current_time_utc + expires_delta
    else:
        expire = current_time_utc + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre session a expiré",
        )
    current_user = get_user_by_id(db, user_id=user_id)
    if current_user is None:
        raise credentials_exception

    return current_user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request,
    db=Depends(get_db),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Votre compte n'est pas activé.",
        )
    resource = request.url.path.split("/")[3]
    authorization = check_permission(
        db=db,
        role=current_user.role.name,
        action=request.method.lower(),
        resource=resource,
    )

    if request.url.path not in basic_authorizations and not authorization:
        LOGGER(
            f"verboten to {request.method.lower()} on {resource} for {current_user.role.name}",
            request,
        )
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à effectuer cette action sur cette ressource.",
        )

    return current_user
