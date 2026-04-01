# Import des modules nécessaires
import json

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
        chambres_token: str,
        patients_token: str,
    ):

        # Construction du chemin complet avec les paramètres de requête
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_chambres}/{full_path}"

        # Envoi de la requête à l'API
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {chambres_token}"},
            follow_redirects=True,
        )

        if response.status_code != 200:
            try:
                result = response.json()
                detail = result.get("detail", "server_issue")
            except Exception:
                detail = response.text or "server_issue"
            raise HTTPException(
                status_code=response.status_code,
                detail=detail,
            )
        services = response.json()

        patients_ids = set()
        for service in services:
            for chambre in service["chambres"]:
                for reservation in chambre["reservations"]:
                    patients_ids.add(reservation["ref"])

        print(patients_ids)

        if len(patients_ids) > 0:
            ids = []
            for p in patients_ids:
                ids.append({"patient_id": p})

            patients_names_response = await client.post(
                f"{self.url_api_patients}/patients/patients_names",
                headers={"Authorization": f"Bearer {patients_token}"},
                json=ids,
            )
            if patients_names_response.status_code == 200:
                patients_list = patients_names_response.json()
                patients_map = {(p["patient_id"]): p for p in patients_list}

                for service in services:
                    for chambre in service["chambres"]:
                        for reservation in chambre["reservations"]:
                            patient = patients_map.get(int(reservation["ref"]))
                            if patient:
                                reservation["patient"] = patient
                            reservation.pop("ref", None)

        return services
