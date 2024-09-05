from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.settings.config import ACCESS_TOKEN_EXPIRE_MINUTES

from ..dependancies.auth import (
    authenticate_user,
    create_access_token,
    create_session,
    get_current_user,
    get_user,
    signout_current_user,
)
from app.dependancies.db_session import get_db
from app.schemas.user import LoginUser, User
from ..utils.logging_setup import LoggerSetup

# Configuration de l'authentifications
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger_setup = LoggerSetup()
LOGGER = logger_setup.write_log

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# Routes d'authentification
@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    db_user = get_user(db, username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login")
async def login(
    response: Response,
    credentials: Annotated[LoginUser, Body()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": str(user.id), "session_id": create_session(user.id)},
        expires_delta=access_token_expires,
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "all good bro!"}


@router.post("/logout")
async def logout(
    response: Response, request: Request, current_user: User = Depends(get_current_user)
):
    return signout_current_user(request, response)


@router.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"role": current_user.role.name}
