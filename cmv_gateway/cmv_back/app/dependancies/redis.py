# Import du module Redis asynchrone
from redis import asyncio as aioredis

# Import de la configuration Valkey
from app.utils.config import VALKEY_HOST, VALKEY_PORT

print(f"HELLO VALKEY CONFIG: {VALKEY_HOST}:{VALKEY_PORT}")

# Configuration du client Redis connecté à Valkey
redis_client = aioredis.from_url(
    f"redis://{VALKEY_HOST}:{VALKEY_PORT}", decode_responses=True
)
