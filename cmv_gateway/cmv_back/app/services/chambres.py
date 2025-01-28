# Import des modules nécessaires
import httpx

from fastapi import HTTPException, Request

from app.utils.config import CHAMBRES_SERVICE


def get_chambres_service():
    """
    Factory function pour créer une instance du service des chambres
    Returns:
        ChambresService: Une nouvelle instance du service
    """
    print(CHAMBRES_SERVICE)
    return ChambresService(url_api_chambres=CHAMBRES_SERVICE)


class ChambresService:
    """Service gérant les interactions avec l'API des chambres"""

    def __init__(
        self,
        url_api_chambres: str,
    ):
        """
        Initialise le service avec l'URL de l'API des chambres
        Args:
            url_api_chambres (str): URL de base de l'API des chambres
        """
        self.url_api_chambres = url_api_chambres

    async def get_chambres(
        self, path: str, request: Request, client: httpx.AsyncClient
    ):
        """
        Récupère les informations des chambres depuis l'API
        Args:
            path (str): Chemin de la requête
            request (Request): Requête FastAPI
            client (httpx.AsyncClient): Client HTTP pour les requêtes
        Returns:
            dict: Données des chambres
        Raises:
            HTTPException: En cas d'erreur de l'API
        """
        # Construction du chemin complet avec les paramètres de requête
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_chambres}/{full_path}"

        # Envoi de la requête à l'API
        response = await client.get(
            url,
            # headers={"Authorization": f"Bearer {internal_token}"},
            follow_redirects=True,
        )
        if response.status_code == 200:
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )
