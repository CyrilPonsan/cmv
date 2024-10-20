import httpx

from fastapi import HTTPException

from app.utils.config import PATIENTS_SERVICE
from app.utils.logging_setup import LoggerSetup


# Initialisation du service patients
def get_patients_service():
    return PatientsService(url_api_patients=PATIENTS_SERVICE)


class PatientsService:
    logger = LoggerSetup()

    def __init__(
        self,
        url_api_patients: str,
    ):
        self.url_api_patients = url_api_patients

    async def get_patients(
        self,
        path: str,
        cookie: dict,
        client: httpx.AsyncClient,
    ):
        print(f"Cookie : {cookie}")
        url = f"{self.url_api_patients}/{path}/"
        response = await client.get(
            url,
            cookies=cookie,
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
