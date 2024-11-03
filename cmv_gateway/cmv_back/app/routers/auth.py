from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.schemas.schemas import Message
from app.schemas.user import Credentials
from app.services.auth import get_auth_service

# Configuration de l'authentifications
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# Permet à un utilisateur enregistré de se connecter à l'application
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


# Déconnecte un utilisateur authentifié de l'application
# Supprime le cookie, la session et blacklist le token dans le service de stockage en mémoire
@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    # current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    return await auth_service.signout(request, response)


# Route pour rafraîchir le token
@router.get("/refresh", response_model=Message)
async def refresh(
    request: Request,
    response: Response,
    auth_service=Depends(get_auth_service),
):
    return await auth_service.refresh(request, response)
