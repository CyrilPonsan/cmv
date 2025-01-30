from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.schemas.reservation import CreateReservation
from app.services.chambres import get_chambres_service
from app.schemas.services import ChambreAvailable
from app.schemas.schemas import SuccessWithMessage
from app.sql.models import Status

# Création du routeur pour les endpoints liés aux chambres
router = APIRouter(
    prefix="/chambres",
    tags=["chambres"],
)


@router.get("/{service_id}", response_model=ChambreAvailable)
async def get_available_room(
    service_id: int,
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    """
    Récupère une chambre disponible pour un service donné.

    Args:
        service_id (int): Identifiant du service
        service_chambre: Service de gestion des chambres
        db (Session): Session de base de données

    Returns:
        ChambreAvailable: Les informations de la chambre disponible
    """
    return await service_chambre.get_available_room(db=db, service_id=service_id)


@router.post("/{chambre_id}/reserver", status_code=201)
async def rerserver_chambre(
    chambre_id: int,
    data: Annotated[CreateReservation, Body()],
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    """
    Crée une réservation pour une chambre.

    Args:
        chambre_id (int): Identifiant de la chambre à réserver
        data (CreateReservation): Données de la réservation
        service_chambre: Service de gestion des chambres
        db (Session): Session de base de données

    Returns:
        ReservationResponse: Les détails de la réservation créée
    """
    return await service_chambre.post_reservation(
        db=db, chambre_id=chambre_id, reservation_data=data
    )


@router.put("/{chambre_id}", response_model=SuccessWithMessage)
async def update_chambre_status(
    chambre_id: int,
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    await service_chambre.update_chambre_status(db, chambre_id, Status.LIBRE)
    return {"success": True, "message": "Chambre mise à jour"}


@router.delete(
    "/{reservation_id}/{chambre_id}/cancel",
    status_code=200,
    response_model=SuccessWithMessage,
)
async def cancel_reservation(
    chambre_id: int,
    reservation_id: int | None = None,
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    """
    Annule une réservation et libère la chambre.

    Args:
        reservation_id (int): Identifiant de la réservation à annuler
        chambre_id (int): Identifiant de la chambre à libérer
        patient_id (int): Identifiant du patient
        service_chambre: Service de gestion des chambres
        db (Session): Session de base de données

    Returns:
        SuccessWithMessage: Message indiquant le succès ou l'échec de l'opération
    """

    return await service_chambre.cancel_reservation(
        db=db,
        reservation_id=reservation_id,
        chambre_id=chambre_id,
    )
