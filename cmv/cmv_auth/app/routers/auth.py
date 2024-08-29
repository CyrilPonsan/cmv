from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from app.dependancies.auth import authenticate_user, create_or_renew_session
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


@router.post("/login")
def login(response: Response, username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    session_id = create_or_renew_session(db, user.id)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return {"message": "Logged in successfully"}


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
