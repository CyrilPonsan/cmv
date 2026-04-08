# Import des modules nécessaires

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.schemas.services import ServicesListItem
from app.sql.models import Chambre, Reservation, Service


# Implémentation concrète pour PostgreSQL
class PgServiceRepository:
    async def read_all_services(self, db: Session):
    async def read_all_services(self, db: Session, service_id: int):
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
            )
            .filter(Service.id_service == service_id)
            # Tri par ID de service
            .order_by(Service.id_service)
            # Élimination des doublons
            .distinct()
            # Exécution de la requête
            .all()
        )

    async def get_simple_services_list(self, db: Session) -> list[Service]:
        """
        Récupère tous les services depuis la base PostgreSQL
        Args:
            db (Session): Session de base de données
        Returns:
            list[Service]: Liste de tous les services
        """
        return db.query(Service).all()
