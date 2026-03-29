"""
Module utilitaire pour le rate limiting de la gateway.

Fournit l'identification client par IP, le callback HTTP 429 personnalisé,
et les fonctions d'initialisation/fermeture du rate limiter avec Valkey.

Utilise fastapi-limiter 0.2.0 qui s'appuie sur pyrate_limiter avec
RedisBucket comme backend de stockage.
"""

import math
import time
import logging

from fastapi import HTTPException, Request, Response
from redis import asyncio as aioredis
from pyrate_limiter import Limiter, Rate, Duration
from pyrate_limiter.buckets.redis_bucket import RedisBucket

from app.utils.config import VALKEY_HOST, VALKEY_PORT

# Logger applicatif
logger = logging.getLogger("CMV_GATEWAY")

# Constantes de configuration du rate limiting
LOGIN_RATE_LIMIT_TIMES = 5
LOGIN_RATE_LIMIT_SECONDS = 60
GLOBAL_RATE_LIMIT_TIMES = 60
GLOBAL_RATE_LIMIT_SECONDS = 60

# Client Redis global pour le rate limiter
_redis_client: aioredis.Redis | None = None

# Limiter instances (initialisés au startup)
global_limiter: Limiter | None = None
login_limiter: Limiter | None = None


async def custom_identifier(request: Request) -> str:
    """Identifie le client par son adresse IP.

    Extrait l'IP depuis l'en-tête X-Forwarded-For (première IP) si présent,
    sinon utilise request.client.host. Retourne "unknown" si l'IP ne peut
    être déterminée.

    Args:
        request: La requête HTTP entrante.

    Returns:
        L'adresse IP du client ou "unknown".
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        return ip

    if request.client and request.client.host:
        return request.client.host

    logger.warning("Impossible de déterminer l'IP du client pour le rate limiting")
    return "unknown"


async def custom_callback(request: Request, response: Response):
    """Callback appelé quand la limite de requêtes est dépassée.

    Lève une HTTPException 429 avec les en-têtes informatifs et un message
    en français indiquant le temps d'attente.

    Args:
        request: La requête HTTP entrante.
        response: La réponse HTTP.

    Raises:
        HTTPException: Toujours levée avec le code 429.
    """
    retry_after = 60
    reset_timestamp = int(time.time()) + retry_after

    raise HTTPException(
        status_code=429,
        detail=f"Trop de requêtes. Réessayez dans {retry_after} secondes.",
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(GLOBAL_RATE_LIMIT_TIMES),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_timestamp),
        },
    )


async def init_rate_limiter() -> bool:
    """Initialise le rate limiter avec une connexion Valkey.

    Crée un client Redis asynchrone et initialise les Limiter instances
    avec RedisBucket pour le rate limiting global et login.

    Returns:
        True si l'initialisation réussit, False sinon.
    """
    global _redis_client, global_limiter, login_limiter

    try:
        _redis_client = aioredis.from_url(
            f"redis://{VALKEY_HOST}:{VALKEY_PORT}",
            encoding="utf-8",
            decode_responses=True,
        )
        # Vérifier la connexion
        await _redis_client.ping()

        # Créer les buckets Redis pour chaque niveau de limitation
        global_rate = Rate(GLOBAL_RATE_LIMIT_TIMES, Duration.MINUTE)
        global_bucket = await RedisBucket.init(
            [global_rate], _redis_client, "rate_limit:global"
        )
        global_limiter = Limiter(global_bucket)

        login_rate = Rate(LOGIN_RATE_LIMIT_TIMES, Duration.MINUTE)
        login_bucket = await RedisBucket.init(
            [login_rate], _redis_client, "rate_limit:login"
        )
        login_limiter = Limiter(login_bucket)

        logger.info(
            f"Rate limiter initialisé avec Valkey ({VALKEY_HOST}:{VALKEY_PORT})"
        )
        return True
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error(
            f"Échec de connexion à Valkey pour le rate limiter: {e}. "
            "Démarrage en mode dégradé sans rate limiting."
        )
        _redis_client = None
        global_limiter = None
        login_limiter = None
        return False


async def close_rate_limiter():
    """Ferme proprement la connexion Redis du rate limiter."""
    global _redis_client, global_limiter, login_limiter

    if global_limiter is not None:
        global_limiter.close()
        global_limiter = None

    if login_limiter is not None:
        login_limiter.close()
        login_limiter = None

    if _redis_client is not None:
        try:
            await _redis_client.aclose()
            logger.info("Connexion Redis du rate limiter fermée.")
        except Exception as e:
            logger.warning(f"Erreur lors de la fermeture de la connexion Redis: {e}")
        finally:
            _redis_client = None
