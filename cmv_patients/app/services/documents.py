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
    documents_repository: PgDocumentsRepository

    def __init__(self, documents_repository: PgDocumentsRepository):
        self.documents_repository = documents_repository

    async def create_document(
        self,
        db: Session,
        file_contents: bytes,
        type_document: DocumentType,
        patient_id: int,
    ):
        patient_service = get_patients_service()
        patient = await patient_service.detail_patient(db=db, patient_id=patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )

        unique_filename = f"{patient_id}_{uuid.uuid4()}.pdf"
        await self._upload_file_to_s3(unique_filename, file_contents)
        return await self.documents_repository.create_document(
            db=db,
            file_name=unique_filename,
            type_document=type_document,
            patient_id=patient_id,
        )

    # Methode pour téléverser un fichier vers un bucket S3 AWS
    async def _upload_file_to_s3(self, file_name: str, file_contents: bytes):
        print(f"AWS BUCKET NAME: {AWS_BUCKET_NAME}")
        if not AWS_BUCKET_NAME:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS bucket name is not configured",
            )

        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )
            file_obj = BytesIO(file_contents)

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
