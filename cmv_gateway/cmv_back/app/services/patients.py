import httpx

from fastapi import HTTPException, Request, Response, UploadFile

from app.schemas.user import User
from app.utils.config import PATIENTS_SERVICE
from app.utils.logging_setup import LoggerSetup


# Initialisation du service patients
def get_patients_service():
    """
    Crée et retourne une instance du service patients avec l'URL configurée
    """
    return PatientsService(url_api_patients=PATIENTS_SERVICE)


class PatientsService:
    """
    Service gérant les interactions avec l'API Patients
    Permet de récupérer, créer et transférer des documents patients
    """

    logger = LoggerSetup()

    def __init__(
        self,
        url_api_patients: str,
    ):
        """
        Initialise le service avec l'URL de l'API patients
        """
        self.url_api_patients = url_api_patients

    async def get_patients(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """
        Récupère les informations patients via l'API

        Args:
            current_user: Utilisateur courant faisant la requête
            path: Chemin de l'endpoint à appeler
            internal_token: Token d'authentification
            client: Client HTTP pour faire les requêtes
            request: Requête FastAPI originale

        Returns:
            Les données patients ou le PDF si c'est un document
        """
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
        """
        Crée ou met à jour des informations patients via l'API

        Args:
            current_user: Utilisateur courant faisant la requête
            path: Chemin de l'endpoint à appeler
            internal_token: Token d'authentification
            client: Client HTTP pour faire les requêtes
            request: Requête FastAPI originale

        Returns:
            La réponse de l'API patients
        """
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
        """
        Transfère un document vers l'API patients

        Args:
            current_user: Utilisateur courant faisant la requête
            path: Chemin de l'endpoint à appeler
            internal_token: Token d'authentification
            file: Fichier à transférer
            document_type: Type du document
            request: Requête FastAPI originale

        Returns:
            La réponse de l'API patients après le transfert
        """
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
