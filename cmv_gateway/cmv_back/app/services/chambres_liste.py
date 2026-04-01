# Import des modules nécessaires
import httpx
from fastapi import HTTPException, Request

from app.utils.config import CHAMBRES_SERVICE, PATIENTS_SERVICE


def get_chambres_liste_service():

    return ChambresListeService(
        url_api_chambres=CHAMBRES_SERVICE, url_api_patients=PATIENTS_SERVICE
    )


class ChambresListeService:
    def __init__(
        self,
        url_api_chambres: str,
        url_api_patients: str,
    ):

        self.url_api_chambres = url_api_chambres
        self.url_api_patients = url_api_patients

    async def get_chambres(
        self,
        path: str,
        request: Request,
        client: httpx.AsyncClient,
        internal_token: str,
    ):

        # Construction du chemin complet avec les paramètres de requête
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_chambres}/{full_path}"

        # Envoi de la requête à l'API
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {internal_token}"},
            follow_redirects=True,
        )
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )
