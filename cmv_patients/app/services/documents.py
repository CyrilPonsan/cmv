from io import BytesIO
import uuid


import boto3
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.documents_crud import PgDocumentsRepository
from app.services.patients import get_patients_service
from app.sql.models import DocumentType
from app.utils.config import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
)


# Retourne une instance de la classe PgDocumentsRepository
def get_documents_repository():
    return PgDocumentsRepository()


# Retourne une instance de la classe DocumentsService
def get_documents_service():
    return DocumentsService(get_documents_repository())


# Service gérant les opérations liées aux documents
class DocumentsService:
    # Repository pour interagir avec la base de données
    documents_repository: PgDocumentsRepository

    def __init__(self, documents_repository: PgDocumentsRepository):
        self.documents_repository = documents_repository

    # Crée un nouveau document pour un patient
    # Params:
    # - db: Session de base de données
    # - file_contents: Contenu binaire du fichier
    # - type_document: Type de document (enum DocumentType)
    # - patient_id: ID du patient
    # Returns: Le document créé
    # Raises: HTTPException si le patient n'existe pas ou en cas d'erreur
    async def create_document(
        self,
        db: Session,
        file_contents: bytes,
        type_document: DocumentType,
        patient_id: int,
    ):
        # Vérifie que le patient existe
        patient_service = get_patients_service()
        patient = await patient_service.detail_patient(db=db, patient_id=patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )

        # Génère un nom de fichier unique avec UUID
        unique_filename = f"{patient_id}_{uuid.uuid4()}.pdf"
        # Upload le fichier sur S3
        await self._upload_file_to_s3(unique_filename, file_contents)
        # Crée l'entrée en base de données
        return await self.documents_repository.create_document(
            db=db,
            file_name=unique_filename,
            type_document=type_document,
            patient_id=patient_id,
        )

    # Téléverse un fichier vers un bucket S3 AWS
    # Params:
    # - file_name: Nom du fichier à créer sur S3
    # - file_contents: Contenu binaire du fichier
    # Returns: True si succès
    # Raises: HTTPException en cas d'erreur de configuration ou d'upload
    async def _upload_file_to_s3(self, file_name: str, file_contents: bytes):
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

    # Télécharge un fichier depuis S3 AWS
    async def download_file_from_s3(self, db: Session, document_id: int):
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
