# Import des modules nécessaires
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


# Implémentation concrète pour PostgreSQL héritant de ServiceRepository
class PgServiceRepository(ServiceRepository):
    async def read_all_services(self, db: Session) -> list[Service]:
        """
        Récupère tous les services depuis la base PostgreSQL avec leurs chambres
        et réservations en cours

        Args:
            db (Session): Session de base de données active

        Returns:
            list[Service]: Liste de tous les services avec leurs relations chargées
        """
        # Récupération de la date/heure actuelle pour filtrer les réservations
        now = datetime.now()

        # Construction et exécution de la requête
        return (
            # Requête de base sur la table Service
            db.query(Service)
            # Jointure avec la table Chambre
            .join(Chambre, Service.id_service == Chambre.service_id)
            # Configuration du chargement des relations
            .options(
                # Chargement des chambres associées au service
                joinedload(Service.chambres)
                # Chargement des réservations en cours pour chaque chambre
                .joinedload(
                    Chambre.reservations.and_(
                        and_(
                            # Filtre sur les réservations actuelles
                            Reservation.entree_prevue <= now,
                            Reservation.sortie_prevue >= now,
                        )
                    )
                )
                # Chargement des informations du patient pour chaque réservation
                .joinedload(Reservation.patient)
            )
            # Tri par ID de service
            .order_by(Service.id_service)
            # Élimination des doublons
            .distinct()
            # Exécution de la requête
            .all()
        )
