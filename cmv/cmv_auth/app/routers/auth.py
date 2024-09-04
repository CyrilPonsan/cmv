from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.settings.models import UserSession

from ..dependancies.auth import (
    authenticate_user,
    create_access_token,
    create_session,
    get_current_user,
    get_user,
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
    request: Request,
    credentials: Annotated[LoginUser, Body()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    session_id = create_session(user.id)
    access_token = create_access_token(data={"sub": user.id, "session_id": session_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/logout")
def logout(
    response: Response,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    session = db.query(UserSession).filter(UserSession.user_id == user.id).first()
    if session:
        db.delete(session)
        db.commit()
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}


@router.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"role": current_user.role.name}
