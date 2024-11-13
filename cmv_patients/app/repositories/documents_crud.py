from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.sql.models import Document, DocumentType


# Interface pour les opérations liées aux documents
class DocumentsRead(ABC):
    @abstractmethod
    async def create_document(
        self, db: Session, file_name: str, type_document: DocumentType, patient_id: int
    ) -> dict:
        pass


# Interface pour les opérations liées aux documents
class DocumentsRepository(DocumentsRead):
    @abstractmethod
    async def create_document(
        self, db: Session, file_name: str, type_document: DocumentType, patient_id: int
    ) -> dict:
        pass


# Repository pour accéder aux données des documents
class PgDocumentsRepository(DocumentsRepository):
    # Méthode pour créer un document
    async def create_document(
        self, db: Session, file_name: str, type_document: DocumentType, patient_id: int
    ) -> Document:
        document = Document(
            nom_fichier=file_name, type_document=type_document, patient_id=patient_id
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return {"message": "Document créé avec succès"}

    # Méthode pour récupérer un document par son ID
    async def get_document_by_id(self, db: Session, document_id: int) -> Document:
        return db.query(Document).filter(Document.id_document == document_id).first()
