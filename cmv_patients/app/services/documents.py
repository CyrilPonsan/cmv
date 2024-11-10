from fastapi import Request
from sqlalchemy.orm import Session

from app.repositories.documents_crud import PgDocumentsRepository
from app.schemas.user import InternalPayload


# Retourne une instance de la classe PgDocumentsRepository
def get_documents_repository():
    pass


# Retourne une instance de la classe DocumentsService
def get_documents_service():
    pass


# Service gérant les opérations liées aux documents
class DocumentsService:
    documents_repository: PgDocumentsRepository

    def __init__(self, documents_repository: PgDocumentsRepository):
        self.documents_repository = documents_repository
