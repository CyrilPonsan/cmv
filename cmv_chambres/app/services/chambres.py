from typing import Annotated

from fastapi import Body, HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.chambres_crud import PgChambresRepository
from app.schemas.reservation import CreateReservation, ReservationResponse
from app.schemas.schemas import SuccessWithMessage
from app.sql.models import Chambre, Status


def get_chambres_repository():
    """Retourne une instance du repository PostgreSQL pour les chambres"""
    return PgChambresRepository()


def get_chambres_service():
    """Retourne une instance du service de gestion des chambres"""
    return ChambresService(get_chambres_repository())


class ChambresService:
    """Service gérant la logique métier liée aux chambres d'hôpital"""

    # Repository pour accéder aux données des chambres
    chambres_repository: PgChambresRepository

    def __init__(self, chambres_repository: PgChambresRepository):
        """Initialise le service avec un repository de chambres"""
        self.chambres_repository = chambres_repository

    async def get_available_room(self, db: Session, service_id: int) -> Chambre:
        """
        Récupère une chambre disponible pour un service donné

        Args:
            db (Session): Session de base de données
            service_id (int): ID du service hospitalier

        Returns:
            Chambre: Une chambre disponible

        Raises:
            HTTPException: Si aucune chambre n'est disponible
        """
        print("chambre")
        # Recherche d'une chambre disponible dans le service
        chambre = await self.chambres_repository.get_available_room(db, service_id)
        print("chambre")
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no_room_available",
            )
        # Marque la chambre comme occupée
        return chambre

    async def update_chambre_status(
        self, db: Session, chambre_id, chambre_status: Status
    ):
        """
        Met à jour le statut d'une chambre

        Args:
            db (Session): Session de base de données
            chambre_id (int): ID de la chambre à mettre à jour
            chambre_status (Status): Nouveau statut de la chambre

        Returns:
            Chambre: La chambre mise à jour
        """
        return await self.chambres_repository.update_chambre_status(
            db, chambre_id, chambre_status
        )

    async def post_reservation(
        self,
        db: Session,
        service_id: int,
        reservation_data: Annotated[CreateReservation, Body()],
    ) -> ReservationResponse:
        """
        Crée une nouvelle réservation pour une chambre

        Args:
            db (Session): Session de base de données
            service_id (int): ID du service pour lequel réserver
            reservation_data (CreateReservation): Données de la réservation

        Returns:
            Reservation: La réservation créée

        Raises:
            HTTPException: Si la chambre n'existe pas
        """
        # Vérifie que la chambre existe
        chambre = await self.get_available_room(db, service_id=service_id)

        await self.update_chambre_status(db, chambre.id_chambre, Status.OCCUPEE)

        # Crée la réservation
        reservation = await self.chambres_repository.create_reservation(
            db=db, chambre=chambre, reservation=reservation_data
        )

        # Retourne la réponse formatée
        return ReservationResponse(
            reservation_id=reservation.reservation_id,
            chambre_id=chambre.id_chambre,
            sortie_prevue_le=reservation.sortie_prevue_le,
        )

    async def cancel_reservation(
        self, db: Session, reservation_id: int
    ) -> SuccessWithMessage:
        """
        Annule une réservation et libère la chambre associée

        Args:
            db (Session): Session de base de données
            reservation_id (int): ID de la réservation à annuler
            chambre_id (int): ID de la chambre à libérer

        Returns:
            SuccessWithMessage: Message de succès ou d'erreur
        """
        reservation = None
        # Vérifie que la réservation existe
        reservation = await self.chambres_repository.get_reservation_by_id(
            db=db, reservation_id=reservation_id
        )
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="reservation_not_found",
            )

        # Récupère la chambre associée
        chambre = await self.chambres_repository.get_chambre_by_id(
            db=db, chambre_id=reservation.chambre.id_chambre
        )

        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="chambre_not_found",
            )

        # Libère la chambre
        await self.update_chambre_status(db, chambre.id_chambre, Status.LIBRE)

        # Annule la réservation
        await self.chambres_repository.cancel_reservation(db, reservation_id)

        return SuccessWithMessage(success=True, message="Réservation annulée")
