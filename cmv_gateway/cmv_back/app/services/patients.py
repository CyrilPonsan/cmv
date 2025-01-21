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

    # Initialisation du logger pour tracer les actions
    logger = LoggerSetup()

    def __init__(
        self,
        url_api_patients: str,
    ):
        """
        Initialise le service avec l'URL de l'API patients
        """
        # URL de base de l'API patients
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
        # Construction du chemin complet avec les paramètres de requête
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_patients}/{full_path}"
        print(f"URL : {url}")

        # Appel à l'API patients
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {internal_token}"},
            follow_redirects=True,
        )

        # Journalisation de la requête
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200:
            # Cas spécial pour les documents PDF
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
            # Gestion des erreurs
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
        # Construction du chemin complet avec les paramètres de requête et slash final
        full_path = path.rstrip("/") + "/"
        if request.query_params:
            full_path = f"{full_path}?{request.query_params}"
        url = f"{self.url_api_patients}/{full_path}"
        print(f"URL : {url}")

        # Récupération du corps de la requête
        request_body = await request.json()
        # Si les données sont dans un objet 'data', on les extrait
        if isinstance(request_body, dict) and "data" in request_body:
            request_body = request_body["data"]

        # Envoi de la requête POST à l'API patients
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {internal_token}",
                "Content-Type": "application/json",
            },
            json=request_body,  # Envoi direct des données du patient
            follow_redirects=True,
        )

        # Journalisation de la requête
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            # Gestion des erreurs
            result = response.json()
            print(f"RESULT : {result}")
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )

    async def delete_patients(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """
        Supprime des informations patients via l'API

        Args:
            current_user: Utilisateur courant faisant la requête
            path: Chemin de l'endpoint à appeler
            internal_token: Token d'authentification
            client: Client HTTP pour faire les requêtes
            request: Requête FastAPI originale

        Returns:
            La réponse de l'API patients
        """
        # Construction du chemin complet avec les paramètres de requête
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_patients}/{full_path}"
        print(f"URL : {url}")

        # Envoi de la requête DELETE à l'API patients
        response = await client.delete(
            url,
            headers={"Authorization": f"Bearer {internal_token}"},
        )

        # Journalisation de la requête
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Gestion des erreurs
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
        # Construction de l'URL complète
        full_path = path
        url = f"{self.url_api_patients}/{full_path}"

        # Création d'un client HTTP temporaire pour l'envoi du fichier
        async with httpx.AsyncClient() as client:
            # Envoi du fichier avec les métadonnées
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {internal_token}"},
                data={"document_type": document_type},
                files={"file": (file.filename, file.file, file.content_type)},
            )

        # Journalisation de la requête
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Gestion des erreurs
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )

    async def put_patients(
        self,
        current_user: User,
        path: str,
        internal_token: str,
        client: httpx.AsyncClient,
        request: Request,
    ):
        """
        Met à jour des informations patients via l'API

        Args:
            current_user: Utilisateur courant faisant la requête
            path: Chemin de l'endpoint à appeler
            internal_token: Token d'authentification
            client: Client HTTP pour faire les requêtes
            request: Requête FastAPI originale

        Returns:
            La réponse de l'API patients
        """
        # Construction du chemin complet
        full_path = path
        url = f"{self.url_api_patients}/{full_path}"

        # Récupération du corps de la requête
        request_body = await request.json()
        # Si les données sont dans un objet 'data', on les extrait
        if isinstance(request_body, dict) and "data" in request_body:
            request_body = request_body["data"]

        # Envoi de la requête PUT à l'API patients
        response = await client.put(
            url,
            headers={
                "Authorization": f"Bearer {internal_token}",
                "Content-Type": "application/json",
            },
            json=request_body,  # Envoi direct des données du patient
            follow_redirects=True,
        )

        # Journalisation de la requête
        self.logger.write_log(
            f"{current_user.role.name} - {current_user.id_user} - {request.method} - {path}",
            request=request,
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Gestion des erreurs
            result = response.json()
            print(f"RESULT : {result}")
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )
