from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import joinedload, Session
from app.sql.models import Chambre, Reservation, Service


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
        now = datetime.now()

        return (
            db.query(Service)
            .join(Chambre, Service.id_service == Chambre.service_id)
            .options(
                joinedload(Service.chambres)
                .joinedload(
                    Chambre.reservations.and_(
                        and_(
                            Reservation.entree_prevue <= now,
                            Reservation.sortie_prevue >= now,
                        )
                    )
                )
                .joinedload(Reservation.patient)
            )
            .order_by(Service.id_service)
            .distinct()
            .all()
        )
