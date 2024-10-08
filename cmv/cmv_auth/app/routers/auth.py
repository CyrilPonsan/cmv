from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.utils.config import ACCESS_TOKEN_EXPIRE_MINUTES

from ..dependancies.auth import (
    authenticate_user,
    create_access_token,
    create_session,
    get_current_user,
    signout_current_user,
)
from app.dependancies.db_session import get_db
from app.schemas.user import LoginUser, User
from ..utils.logging_setup import LoggerSetup

# Configuration de l'authentifications
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = LoggerSetup()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    credentials: Annotated[LoginUser, Body()],
    db: Session = Depends(get_db),
):
    user = await authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = await create_access_token(
        data={
            "sub": str(user.id_user),
            "session_id": await create_session(user.id_user),
        },
        expires_delta=access_token_expires,
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    logger.write_log(f"{user.role.name} connection ", request)
    return {"message": "all good bro!"}


@router.get("/users/me", response_model=dict)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"role": current_user.role.name}


@router.post("/logout")
async def logout(
    response: Response, request: Request, current_user: User = Depends(get_current_user)
):
    print("disconnecting...")
    return await signout_current_user(request, response)


"""







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
"""
