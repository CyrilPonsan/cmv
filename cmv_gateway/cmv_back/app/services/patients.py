import httpx

from fastapi import HTTPException, Request, Response, UploadFile

from app.schemas.user import User
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
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_patients}/{full_path}"
        print(f"URL : {url}")
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {internal_token}"},
            follow_redirects=True,
        )
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )
        if response.status_code == 200:
            # Si c'est un PDF, on retourne directement la réponse
            if response.headers.get("content-type") == "application/pdf":
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": response.headers.get(
                            "content-disposition", "inline"
                        )
                    },
                )
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )

    async def post_patients(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_patients}/{full_path}"
        print(f"URL : {url}")
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {internal_token}"},
            json=request.json(),
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
                detail=result["detail"] or "server_issue",
            )

    async def forward_document(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        file: UploadFile,
        document_type: str,
        request: Request,
    ):
        full_path = path
        url = f"{self.url_api_patients}/{full_path}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {internal_token}"},
                data={"document_type": document_type},
                files={"file": (file.filename, file.file, file.content_type)},
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
                detail=result["detail"] or "server_issue",
            )
