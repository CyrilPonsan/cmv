from typing import Annotated

from fastapi import HTTPException, status, Body
from sqlalchemy.orm import Session

from app.repositories.chambres_crud import PgChambresRepository
from app.schemas.reservation import CreateReservation, ReservationResponse
from app.sql.models import Chambre, Status
from app.schemas.schemas import SuccessWithMessage


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
        # Recherche d'une chambre disponible dans le service
        chambre = await self.chambres_repository.get_available_room(db, service_id)
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no_room_available",
            )
        # Marque la chambre comme occupée
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
        # Vérifie que la chambre existe
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
            # Crée un nouveau patient s'il n'existe pas
            patient = await self.chambres_repository.create_patient(
                db, reservation_data.patient
            )
        # Associe le patient à la chambre
        await self.chambres_repository.update_chambre_patient(db, chambre_id, patient)

        # Crée la réservation
        try:
            reservation = await self.chambres_repository.create_reservation(
                db=db, chambre=chambre, patient=patient, reservation=reservation_data
            )
        except Exception as e:
            print(f"ERREUR {e}")
            await self.delete_patient(db, patient.id_patient)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="reservation_not_found",
            )
        # Retourne la réponse formatée
        return ReservationResponse(
            id_chambre=chambre.id_chambre,
            nom=chambre.nom,
            status=chambre.status.value,
            dernier_nettoyage=chambre.dernier_nettoyage,
            service_id=chambre.service_id,
            reservation_id=reservation.id_reservation,
        )

    async def cancel_reservation(
        self, db: Session, reservation_id: int, chambre_id: int, patient_id: int
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

        print("CANCEL RESERVATION")

        # Récupère la chambre associée
        chambre = await self.chambres_repository.get_chambre_by_id(
            db=db, chambre_id=chambre_id
        )

        # Libère la chambre
        await self.update_chambre_status(db, chambre.id_chambre, Status.LIBRE)

        if patient_id:
            await self.delete_patient(db, patient_id)

        # Vérifie que la réservation existe
        if reservation_id:
            reservation = await self.chambres_repository.get_reservation_by_id(
                db=db, reservation_id=reservation_id
            )
            if not reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="reservation_not_found",
                )

        # Annule la réservation
        await self.chambres_repository.cancel_reservation(db, reservation_id)

        # Vérifie si le patient a d'autres réservations
        if patient_id:
            await self.delete_patient(db, patient_id)

        return {"success": True, "message": "Réservation annulée avec succès"}

    async def delete_patient(self, db: Session, patient_id: int) -> SuccessWithMessage:
        # Vérifie si le patient a d'autres réservations
        reservations = await self.chambres_repository.get_reservations(
            db=db, patient_id=patient_id
        )

        # Supprime le patient s'il n'a plus de réservations
        if len(reservations) == 0:
            await self.chambres_repository.delete_patient(db, patient_id)
            return {"success": True, "message": "Patient supprimé avec succès"}
        else:
            return {"success": False, "message": "Patient a des réservations"}
