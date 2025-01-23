from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import uuid
from io import BytesIO
import boto3

from app.repositories.patients_crud import PgPatientsRepository
from app.repositories.documents_crud import PgDocumentsRepository
from app.utils.config import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
)
from app.schemas.schemas import Patient
from app.sql.models import DocumentType


# Retourne une instance du repository pour accéder aux données des patients
def get_patients_repository():
    return PgPatientsRepository()


# Retourne une instance du repository pour accéder aux données des documents
def get_documents_repository():
    return PgDocumentsRepository()


# Retourne une instance du service gérant les patients et leurs documents
def get_patients_service():
    return PatientsService(
        patients_repository=get_patients_repository(),
        documents_repository=get_documents_repository(),
    )


class PatientsService:
    """Service gérant les opérations liées aux patients et leurs documents"""

    # Repository pour accéder aux données des patients
    patients_repository: PgPatientsRepository
    # Repository pour accéder aux données des documents
    documents_repository: PgDocumentsRepository

    def __init__(
        self,
        patients_repository: PgPatientsRepository,
        documents_repository: PgDocumentsRepository,
    ):
        """
        Initialise le service avec un repository de patients et un repository de documents
        Args:
            patients_repository: Repository pour accéder aux données des patients
            documents_repository: Repository pour accéder aux données des documents
        """
        self.patients_repository = patients_repository
        self.documents_repository = documents_repository

    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> dict:
        """
        Récupère la liste paginée de tous les patients
        Args:
            db: Session de base de données
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ sur lequel trier
            order: Ordre de tri (asc/desc)
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            dict: Dictionnaire contenant les patients et leur nombre total
        """
        # Appel au repository pour récupérer les patients avec pagination et tri
        return await self.patients_repository.read_all_patients(
            db=db, page=page, limit=limit, field=field, order=order
        )

    async def detail_patient(self, db: Session, patient_id: int):
        """
        Récupère les détails d'un patient spécifique
        Args:
            db: Session de base de données
            patient_id: ID du patient à récupérer
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            Patient: Les détails du patient demandé
        """
        # Appel au repository pour récupérer les détails d'un patient par son ID
        return await self.patients_repository.read_patient_by_id(
            db=db, patient_id=patient_id
        )

    async def search_patients(
        self,
        db: Session,
        search: str,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> dict:
        """
        Recherche des patients selon des critères
        Args:
            db: Session de base de données
            search: Terme de recherche
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ sur lequel trier
            order: Ordre de tri (asc/desc)
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            dict: Dictionnaire contenant les patients trouvés et leur nombre total
        """
        # Appel au repository pour rechercher des patients avec pagination et tri
        return await self.patients_repository.search_patients(
            db=db, search=search, page=page, limit=limit, field=field, order=order
        )

    async def create_patient(self, db: Session, data: Patient) -> Patient:
        """
        Crée un nouveau patient
        Args:
            db: Session de base de données
            data: Données du patient à créer
        Returns:
            Patient: Le patient créé
        Raises:
            HTTPException: Si le patient existe déjà
        """
        # Vérification si le patient existe déjà
        if await self.patients_repository.check_patient_exists(db, data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="patient_already_exists"
            )
        # Création du patient via le repository
        return await self.patients_repository.create_patient(db, data)

    async def update_patient(
        self, db: Session, patient_id: int, data: Patient
    ) -> Patient:
        """
        Met à jour les données d'un patient existant
        Args:
            db: Session de base de données
            patient_id: ID du patient à mettre à jour
            data: Nouvelles données du patient
        Returns:
            Patient: Le patient mis à jour
        Raises:
            HTTPException: Si le patient n'existe pas
        """
        if not await self.patients_repository.read_patient_by_id(
            db=db, patient_id=patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )
        return await self.patients_repository.update_patient(db, patient_id, data)

    async def delete_patient(self, db: Session, patient_id: int):
        """
        Supprime un patient
        Args:
            db: Session de base de données
            patient_id: ID du patient à supprimer
        Returns:
            dict: Message de confirmation
        """
        patient = await self.patients_repository.read_patient_by_id(db, patient_id)
        documents = patient.documents
        for document in documents:
            await self.delete_document_by_id(db, document.id_document)
        return await self.patients_repository.delete_patient(db, patient_id)

    async def create_patient_document(
        self,
        db: Session,
        file_contents: bytes,
        type_document: DocumentType,
        patient_id: int,
    ) -> dict:
        """
        Crée un nouveau document pour un patient
        Args:
            db: Session de base de données
            file_contents: Contenu binaire du fichier PDF
            type_document: Type de document (enum DocumentType)
            patient_id: ID du patient associé au document
        Returns:
            dict: Informations sur le document créé
        Raises:
            HTTPException: Si le patient n'existe pas ou en cas d'erreur
        """
        # Vérification que le patient existe
        patient = await self.patients_repository.read_patient_by_id(
            db=db, patient_id=patient_id
        )
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )

        # Génération du nom de fichier unique
        unique_filename = f"{patient_id}_{uuid.uuid4()}.pdf"

        # Upload du fichier sur S3
        await self._upload_file_to_s3(unique_filename, file_contents)

        # Création de l'entrée en base de données
        return await self.documents_repository.create_document(
            db=db,
            file_name=unique_filename,
            type_document=type_document,
            patient_id=patient_id,
        )

    async def get_patient_document(self, db: Session, document_id: int):
        """
        Récupère un document d'un patient
        Args:
            db: Session de base de données
            document_id: ID du document à récupérer
        Returns:
            BytesIO: Contenu du document
        Raises:
            HTTPException: Si le document n'existe pas
        """
        document = await self.documents_repository.get_document_by_id(
            db=db, document_id=document_id
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="document_not_found"
            )
        return await self._download_file_from_s3(document)

    async def delete_patient_document(self, db: Session, document_id: int) -> dict:
        """
        Supprime un document d'un patient
        Args:
            db: Session de base de données
            document_id: ID du document à supprimer
        Returns:
            dict: Message de confirmation
        Raises:
            HTTPException: Si le document n'existe pas
        """
        document = await self.documents_repository.get_document_by_id(
            db=db, document_id=document_id
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="document_not_found"
            )

        # Suppression du fichier S3
        await self._delete_file_from_s3(document.nom_fichier)

        # Suppression de l'entrée en base
        return await self.documents_repository.delete_document_by_id(
            db=db, document_id=document_id
        )

    async def _upload_file_to_s3(self, file_name: str, file_contents: bytes):
        """
        Téléverse un fichier vers un bucket S3 AWS
        Args:
            file_name: Nom du fichier à créer sur S3
            file_contents: Contenu binaire du fichier
        Returns:
            bool: True si succès
        Raises:
            HTTPException: En cas d'erreur de configuration ou d'upload
        """
        # Vérifie que le bucket S3 est configuré
        if not AWS_BUCKET_NAME:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS bucket name is not configured",
            )

        try:
            # Initialise le client S3
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )

            print("AWS Configuration:")
            print(f"Bucket: {AWS_BUCKET_NAME}")
            print(f"Region: {AWS_REGION}")
            print(f"Access Key ID: {AWS_ACCESS_KEY_ID[:4]}...")

            # Convertit les bytes en objet fichier
            file_obj = BytesIO(file_contents)

            # Upload le fichier sur S3
            s3_client.upload_fileobj(
                file_obj,
                AWS_BUCKET_NAME,
                file_name,
                ExtraArgs={"ContentType": "application/pdf"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3: {str(e)}",
            )
        return True

    async def download_file_from_s3(self, db: Session, document_id: int):
        """
        Télécharge un fichier depuis S3 AWS
        Args:
            db: Session de base de données
            document_id: ID du document à télécharger
        Returns:
            tuple: (BytesIO, str) Contenu du fichier et nom du fichier
        Raises:
            HTTPException: Si le document n'existe pas ou en cas d'erreur
        """
        existing_document = await self.documents_repository.get_document_by_id(
            db=db, document_id=document_id
        )
        if not existing_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="document_not_found"
            )

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        file_obj = BytesIO()
        s3_client.download_fileobj(
            AWS_BUCKET_NAME, existing_document.nom_fichier, file_obj
        )

        # Reset le curseur et retourne l'objet BytesIO directement au lieu de getvalue()
        file_obj.seek(0)
        return file_obj, existing_document.nom_fichier

    async def delete_document_by_id(self, db: Session, document_id: int):
        """
        Supprime un document par son ID
        Args:
            db: Session de base de données
            document_id: ID du document à supprimer
        Returns:
            dict: Message de confirmation
        Raises:
            HTTPException: Si le document n'existe pas
        """
        # Vérifie si le document existe dans la base de données
        existing_document = await self.documents_repository.get_document_by_id(
            db=db, document_id=document_id
        )
        # Si le document n'existe pas, lève une exception 404
        if not existing_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="document_not_found"
            )

        # Initialise le client S3 avec les credentials AWS
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        # Supprime le fichier du bucket S3 en utilisant le nom du fichier comme clé
        s3_client.delete_object(
            Bucket=AWS_BUCKET_NAME, Key=existing_document.nom_fichier
        )

        # Supprime l'entrée du document dans la base de données et retourne le résultat
        return await self.documents_repository.delete_document_by_id(
            db=db, document_id=document_id
        )
