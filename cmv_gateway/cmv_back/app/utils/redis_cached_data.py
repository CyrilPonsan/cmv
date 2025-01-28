# Import des modules nécessaires
import json
from functools import wraps
import asyncio

# Import du client Redis
from app.dependancies.redis import redis_client


def cache_data(expire_time: int, key: str):
    """
    Décorateur pour mettre en cache les données avec Redis.

    Args:
        expire_time (int): Durée de validité du cache en secondes
        key (str): Clé utilisée pour stocker les données dans Redis

    Returns:
        wrapper: Fonction décorée avec gestion du cache
    """

    def decorator(func):
        @wraps(func)
        async def wrapper():
            try:
                # Tentative de récupération des données depuis le cache
                cached_data = await redis_client.get(key)
                if cached_data:
                    # Si les données sont en cache, on les retourne directement
                    return json.loads(cached_data)

                # Si pas de données en cache, on exécute la fonction
                if asyncio.iscoroutinefunction(func):
                    # Cas d'une fonction asynchrone
                    data = await func()
                else:
                    # Cas d'une fonction synchrone
                    data = func()

                # Stockage des données dans le cache avec expiration
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
