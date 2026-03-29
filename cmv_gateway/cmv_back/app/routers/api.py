# Import du module FastAPI pour la gestion des routes
import logging

from fastapi import APIRouter, Depends, Request, Response
from redis.exceptions import RedisError

from fastapi_limiter.depends import RateLimiter

# Import des différents modules de routage
from app.routers import chambres, ml
from app.utils.rate_limiter import (
    custom_identifier,
    custom_callback,
)
from . import auth, patients, users

logger = logging.getLogger("CMV_GATEWAY")


async def global_rate_limit(request: Request, response: Response):
    """Dépendance de rate limiting global.

    Applique la limite de 60 req/60s si le limiter est initialisé.
    En mode dégradé (Valkey indisponible), laisse passer la requête.
    """
    from app.utils.rate_limiter import global_limiter

    if global_limiter is not None:
        checker = RateLimiter(
            limiter=global_limiter,
            identifier=custom_identifier,
            callback=custom_callback,
        )
        try:
            await checker(request, response)
        except (RedisError, ConnectionError, TimeoutError, OSError) as e:
            logger.warning(
                "Rate limiting global temporairement désactivé (Valkey indisponible): %s", e
            )


# Création du routeur principal avec préfixe /api et rate limiting global
router = APIRouter(
    prefix="/api",
    tags=["api"],
    dependencies=[Depends(global_rate_limit)],
)


# Inclusion des sous-routeurs pour chaque fonctionnalité
router.include_router(auth.router)  # Routes d'authentification
router.include_router(chambres.router)  # Routes de gestion des chambres
router.include_router(patients.router)  # Routes de gestion des patients
router.include_router(users.router)  # Routes de gestion des utilisateurs
router.include_router(ml.router)  # Routes de prédiction ML
