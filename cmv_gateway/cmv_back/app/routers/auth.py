# Import des modules nécessaires
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Import des dépendances et schémas
from app.dependancies.db_session import get_db
from app.schemas.schemas import Message, SuccessWithMessage
from app.schemas.user import Credentials
from app.services.auth import get_auth_service

# Configuration du contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration du routeur d'authentification
router = APIRouter(
    prefix="/auth",  # Préfixe pour toutes les routes d'authentification
    tags=["auth"],  # Tag pour le regroupement dans la documentation
)


@router.post("/login", response_model=SuccessWithMessage)
async def login(
    request: Request,  # Requête HTTP entrante
    response: Response,  # Réponse HTTP à renvoyer
    credentials: Annotated[
        Credentials, Body()
    ],  # Corps de la requête contenant les identifiants
    auth_service=Depends(get_auth_service),  # Service d'authentification
    db: Session = Depends(get_db),  # Session de base de données
):
    """
    Point d'entrée pour la connexion d'un utilisateur.
    Vérifie les identifiants et crée une session si valides.
    """
    await auth_service.login(
        db=db,
        request=request,
        response=response,
        username=credentials.username,
        password=credentials.password,
    )

    return {"success": True, "message": "all good bro!"}


@router.post("/logout")
async def logout(
    response: Response,  # Réponse HTTP à renvoyer
    request: Request,  # Requête HTTP entrante
    # current_user: User = Depends(get_current_user),  # Utilisateur actuellement connecté
    auth_service=Depends(get_auth_service),  # Service d'authentification
):
    """
    Point d'entrée pour la déconnexion d'un utilisateur.
    Supprime le cookie de session, la session active et blacklist le token JWT.
    """
    return await auth_service.signout(request, response)


@router.get("/refresh", response_model=Message)
async def refresh(
    request: Request,  # Requête HTTP entrante
    response: Response,  # Réponse HTTP à renvoyer
    auth_service=Depends(get_auth_service),  # Service d'authentification
):
    """
    Point d'entrée pour le rafraîchissement du token JWT.
    Génère un nouveau token si le token de rafraîchissement est valide.
    """
    return await auth_service.refresh(request, response)
