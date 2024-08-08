from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from app.dependancies.auth import authenticate_user
from app.dependancies.db_session import get_db
from app.dependancies.jwt import create_token, get_current_active_user
from app.schemas.schemas import Tokens
from app.schemas.user import User
from ..logging_setup import LoggerSetup
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# vérification des identifiants de l'utilisateur et génération de tokens
@router.post(
    "/login",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    response_model=Tokens,
)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        LOGGER("Echec de la tentative de connexion", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return get_tokens(user.id)


# vérification de la validité du refresh token et génération de nouveaux tokens
@router.get("/refresh", response_model=Tokens)
async def refresh_tokens(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Problème serveur"
        )
    return get_tokens(current_user.id)


# génère un token d'accès et un token de rafraîchissement
def get_tokens(user_id):
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token(
        data={"sub": str(user_id)}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token}
