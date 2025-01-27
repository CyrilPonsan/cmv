from typing import Annotated

from fastapi import HTTPException, status, Body
from sqlalchemy.orm import Session

from app.repositories.chambres_crud import PgChambresRepository
from app.schemas.reservation import CreateReservation, ReservationResponse
from app.sql.models import Chambre, Status


def get_chambres_repository():
    """Retourne une instance du repository PostgreSQL pour les chambres"""
    return PgChambresRepository()


def get_chambres_service():
    """Retourne une instance du service de gestion des chambres"""
    return ChambresService(get_chambres_repository())


class ChambresService:
    """Service gérant la logique métier liée aux chambres d'hôpital"""

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
        chambre = await self.chambres_repository.get_available_room(db, service_id)
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no_room_available",
            )
        await self.update_chambre_status(db, chambre.id_chambre, Status.OCCUPEE)
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
        chambre_id: int,
        reservation_data: Annotated[CreateReservation, Body()],
    ) -> ReservationResponse:
        """
        Crée une nouvelle réservation pour une chambre

        Args:
            db (Session): Session de base de données
            chambre_id (int): ID de la chambre à réserver
            reservation_data (CreateReservation): Données de la réservation

        Returns:
            Reservation: La réservation créée

        Raises:
            HTTPException: Si la chambre n'existe pas
        """
        chambre = await self.chambres_repository.get_chambre_by_id(db, chambre_id)
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="chambre_not_found",
            )

        # Récupère ou crée le patient associé à la réservation
        patient = await self.chambres_repository.get_patient(
            db, reservation_data.patient.id_patient
        )
        if not patient:
            patient = await self.chambres_repository.create_patient(
                db, reservation_data.patient
            )
        await self.chambres_repository.update_chambre_patient(db, chambre_id, patient)

        await self.chambres_repository.create_reservation(
            db=db, chambre=chambre, patient=patient, reservation=reservation_data
        )

        return ReservationResponse(
            id_chambre=chambre.id_chambre,
            nom=chambre.nom,
            status=chambre.status.value,
            dernier_nettoyage=chambre.dernier_nettoyage,
            service_id=chambre.service_id,
        )
