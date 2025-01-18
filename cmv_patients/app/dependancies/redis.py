# from ..settings.config import ENVIRONMENT

from redis import asyncio as aioredis

from app.utils.config import ENVIRONMENT

print(f"ENVIRONMENT {ENVIRONMENT}")

if ENVIRONMENT == "dev":
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
else:
    redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
