from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.sql.models import Document, DocumentType


# Interface pour les opérations liées aux documents
class DocumentsCrud(ABC):
    @abstractmethod
    async def create_document(
        self, db: Session, file_name: str, type_document: DocumentType, patient_id: int
    ) -> dict:
        pass


# Repository pour accéder aux données des documents
class PgDocumentsRepository(DocumentsCrud):
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
        return {"message": "document_created"}

    # Méthode pour récupérer un document par son ID
    async def get_document_by_id(self, db: Session, document_id: int) -> Document:
        return db.query(Document).filter(Document.id_document == document_id).first()

    # Méthode pour supprimer un document par son ID
    async def delete_document_by_id(self, db: Session, document_id: int) -> Document:
        db.query(Document).filter(Document.id_document == document_id).delete()
        db.commit()
        return {"success": True, "message": "document_deleted"}
