from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.sql.models import Document


# Interface pour les opérations liées aux documents
class DocumentsRead(ABC):
    @abstractmethod
    async def read_all_patient_documents(
        self, db: Session, patient_id: int
    ) -> list[dict]:
        pass


# Interface pour les opérations liées aux documents
class DocumentsRepository(DocumentsRead):
    @abstractmethod
    async def read_all_patient_documents(
        self, db: Session, patient_id: int
    ) -> list[dict]:
        pass


# Repository pour accéder aux données des documents
class PgDocumentsRepository(DocumentsRepository):
    # Fonction de lecture de tous les documents d'un patient
    async def read_all_patient_documents(
        self, db: Session, patient_id: int
    ) -> list[dict]:
        return db.query(Document).filter(Document.patient_id == patient_id).all()
