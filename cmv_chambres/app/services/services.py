# Import des modules nécessaires
from sqlalchemy.orm import Session

# Import des dépendances internes
from app.repositories.service_crud import PgServiceRepository, ServiceRepository
from app.schemas.services import ServicesListItem


def get_service_repository():
    """Retourne une instance du repository PostgreSQL pour les services"""
    return PgServiceRepository()


def get_service_service():
    """Retourne une instance du service de gestion des services hospitaliers"""
    return ServiceService(get_service_repository())


class ServiceService:
    """Service gérant la logique métier liée aux services hospitaliers"""

    # Repository pour accéder aux données des services
    service_repository: ServiceRepository

    def __init__(self, service_repository: ServiceRepository):
        """Initialise le service avec un repository de services

        Args:
            service_repository (ServiceRepository): Repository pour accéder aux données des services
        """
        self.service_repository = service_repository

    async def read_all_services(self, db: Session) -> list[ServicesListItem]:
        """Récupère la liste de tous les services avec leurs chambres

        Args:
            db (Session): Session de base de données

        Returns:
            list[ServicesListItem]: Liste des services avec leurs informations et chambres associées
        """
        return await self.service_repository.read_all_services(db)
