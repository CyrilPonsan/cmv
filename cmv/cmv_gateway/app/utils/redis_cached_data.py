import json
from functools import wraps
import asyncio

from app.dependancies.redis import redis_client


def cache_data(expire_time: int, key: str):
    def decorator(func):
        @wraps(func)
        async def wrapper():
            try:
                cached_data = await redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)

                if asyncio.iscoroutinefunction(func):
                    data = await func()
                else:
                    data = func()
                await redis_client.setex(key, expire_time, json.dumps(data))
                return data

            except Exception as e:
                print(f"Erreur lors de l'utilisation du cache: {e}")
                # En cas d'erreur avec Redis, exécutez simplement la fonction sans cache
                if asyncio.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()

        return wrapper

    return decorator
