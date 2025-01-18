from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.sql.models import Service


# Interface abstraite définissant les opérations CRUD pour les services
class ServiceCrud(ABC):
    @abstractmethod
    async def read_all_services(self, db: Session) -> list[Service]:
        """
        Méthode abstraite pour récupérer tous les services
        Args:
            db (Session): Session de base de données
        Returns:
            list[Service]: Liste de tous les services
        """
        pass


# Classe repository abstraite héritant de ServiceCrud
class ServiceRepository(ServiceCrud):
    @abstractmethod
    async def read_all_services(self, db: Session) -> list[Service]:
        """
        Méthode abstraite pour récupérer tous les services
        Args:
            db (Session): Session de base de données
        Returns:
            list[Service]: Liste de tous les services
        """
        pass


# Implémentation des méthodes des classes abstraites dont elle hérite
class PgServiceRepository(ServiceRepository):
    async def read_all_services(self, db: Session) -> list[Service]:
        """

        Récupère tous les services depuis la base PostgreSQL
        Args:
            db (Session): Session de base de données
        Returns:
            list[Service]: Liste de tous les services
        """
        return db.query(Service).all()
