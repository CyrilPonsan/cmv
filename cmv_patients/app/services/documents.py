from fastapi import Request
from sqlalchemy.orm import Session

from app.repositories.documents_crud import PgDocumentsRepository
from app.schemas.user import InternalPayload
from app.utils.logging_setup import LoggerSetup


# Retourne une instance de la classe PgDocumentsRepository
def get_documents_repository():
    pass


# Retourne une instance de la classe DocumentsService
def get_documents_service():
    pass


# Service gérant les opérations liées aux documents
class DocumentsService:
    logger = LoggerSetup()
    documents_repository: PgDocumentsRepository

    def __init__(self, documents_repository: PgDocumentsRepository):
        self.documents_repository = documents_repository

    # Récupère tous les documents d'un patient
    async def read_all_patient_documents(
        self, db: Session, patient_id: int, request: Request, payload: InternalPayload
    ) -> list[dict]:
        self.logger.write_log(
            f"{payload['role']} - {payload['user_id']} - {request.method} - read documents : {patient_id}",
            request,
        )
        return await self.documents_repository.read_all_patient_documents(
            db, patient_id
        )
