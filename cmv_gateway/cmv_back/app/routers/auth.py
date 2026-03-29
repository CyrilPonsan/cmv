# Import des modules nécessaires
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from redis.exceptions import RedisError
from fastapi_limiter.depends import RateLimiter

# Import des dépendances et schémas
from app.dependancies.db_session import get_db
from app.schemas.schemas import Message, SuccessWithMessage
from app.schemas.user import Credentials
from app.services.auth import get_auth_service
from app.utils.rate_limiter import custom_identifier, custom_callback

logger = logging.getLogger("CMV_GATEWAY")

# Configuration du contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration du routeur d'authentification
router = APIRouter(
    prefix="/auth",  # Préfixe pour toutes les routes d'authentification
    tags=["auth"],  # Tag pour le regroupement dans la documentation
)


async def login_rate_limit(request: Request, response: Response):
    """Dépendance de rate limiting strict pour le login.

    Applique la limite de 5 req/60s si le limiter est initialisé.
    En mode dégradé (Valkey indisponible), laisse passer la requête.
    """
    from app.utils.rate_limiter import login_limiter

    if login_limiter is not None:
        checker = RateLimiter(
            limiter=login_limiter,
            identifier=custom_identifier,
            callback=custom_callback,
        )
        try:
            await checker(request, response)
        except (RedisError, ConnectionError, TimeoutError, OSError) as e:
            logger.warning(
                "Rate limiting login temporairement désactivé (Valkey indisponible): %s", e
            )


@router.post("/login", response_model=SuccessWithMessage, dependencies=[Depends(login_rate_limit)])
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
