# Import du client HTTP asynchrone
from httpx import AsyncClient


async def get_http_client():
    """
    Crée et gère un client HTTP asynchrone.

    Yields:
        AsyncClient: Un client HTTP asynchrone actif

    Note:
        Le client est automatiquement fermé après utilisation grâce au contexte async with
    """
    async with AsyncClient() as client:
        yield client
