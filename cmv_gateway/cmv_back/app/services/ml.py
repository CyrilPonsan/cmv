"""
Service gérant les interactions avec l'API ML de prédiction.
"""

import hashlib
import hmac

import httpx
from fastapi import HTTPException, Request

from app.schemas.user import User
from app.utils.config import HMAC, ML_SERVICE
from app.utils.logging_setup import LoggerSetup


def get_ml_service():
    """Crée et retourne une instance du service ML."""
    return MLService(url_api_ml=ML_SERVICE)


class MLService:
    """
    Service gérant les interactions avec l'API ML.
    Permet de faire des prédictions de durée d'hospitalisation.
    """

    logger = LoggerSetup()

    def __init__(self, url_api_ml: str):
        self.url_api_ml = url_api_ml

    async def get_ml(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """Récupère des données depuis l'API ML (ex: historique des prédictions)."""
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For", "unknown"
        )

        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_ml}/{full_path}"

        response = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {internal_token}",
                "X-Real-IP": client_ip,
                "X-Forwarded-For": client_ip,
            },
            follow_redirects=True,
        )

        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200:
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result.get("detail", "server_issue"),
            )

    async def put_ml(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """Envoie des données à l'API ML (ex: prédiction, validation)."""
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For", "unknown"
        )

        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_ml}/{full_path}"

        request_body = await request.json()

        if "adid" in request_body:
            adid = request_body["adid"]
            hashed_id = hmac.new(
                key=HMAC.encode("utf-8"),
                msg=adid.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            request_body["adid"] = hashed_id
        else:
            return

        response = await client.put(
            url,
            headers={
                "Authorization": f"Bearer {internal_token}",
                "X-Real-IP": client_ip,
                "X-Forwarded-For": client_ip,
                "Content-Type": "application/json",
            },
            json=request_body,
            follow_redirects=True,
        )

        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result.get("detail", "server_issue"),
            )

    async def post_ml(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """Envoie des données à l'API ML (ex: prédiction, validation)."""
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For", "unknown"
        )

        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_ml}/{full_path}"

        request_body = await request.json()

        if "adid" in request_body:
            adid = request_body["adid"]
            hashed_id = hmac.new(
                key=HMAC.encode("utf-8"),
                msg=adid.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            request_body["adid"] = hashed_id

            print(f"HASHED ADID : {hashed_id}")

        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {internal_token}",
                "X-Real-IP": client_ip,
                "X-Forwarded-For": client_ip,
                "Content-Type": "application/json",
            },
            json=request_body,
            follow_redirects=True,
        )

        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result.get("detail", "server_issue"),
            )
