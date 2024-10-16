# from ..settings.config import ENVIRONMENT

from redis import asyncio as aioredis


redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
