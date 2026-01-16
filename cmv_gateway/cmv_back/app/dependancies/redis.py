# Import du module Redis asynchrone
from redis import asyncio as aioredis

# Import de la configuration d'environnement
from app.utils.config import ENVIRONMENT

# Configuration du client Redis en fonction de l'environnement
if ENVIRONMENT != "preprod":
    # En développement, connexion à Redis sur localhost
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
else:
    # En production, connexion à Redis via le service Docker
    redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
