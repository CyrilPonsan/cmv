# Import du module Redis asynchrone
from redis import asyncio as aioredis

# Import de la variable d'environnement
from app.utils.config import ENVIRONMENT

# Affichage de l'environnement actuel pour le debugging
print(f"ENVIRONMENT {ENVIRONMENT}")

# Configuration du client Redis selon l'environnement
if ENVIRONMENT == "dev":
    # En développement, connexion à Redis sur localhost
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
else:
    # En production, connexion au conteneur Redis
    redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
