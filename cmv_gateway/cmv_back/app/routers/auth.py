from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.dependancies.auth import (
    get_current_user,
)
from app.dependancies.db_session import get_db
from app.schemas.user import Credentials, User
from app.services.auth import get_auth_service

# Configuration de l'authentifications
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", response_model=dict)
async def login(
    request: Request,
    response: Response,
    credentials: Annotated[Credentials, Body()],
    auth_service=Depends(get_auth_service),
    db: Session = Depends(get_db),
):
    await auth_service.login(
        db=db,
        request=request,
        response=response,
        username=credentials.username,
        password=credentials.password,
    )
    return {"message": "all good bro!"}


@router.get("/users/me", response_model=dict)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"role": current_user.role.name}


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    return await auth_service.signout(request, response)


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
