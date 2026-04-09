from typing import Annotated

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.reservation import CreateReservation, ReservationResponse
from app.schemas.schemas import SuccessWithMessage
from app.schemas.services import ChambreAvailable
from app.schemas.user import InternalPayload
from app.services.chambres import get_chambres_service
from app.sql.models import Status
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

# Création du routeur pour les endpoints liés aux chambres
router = APIRouter(
    prefix="/chambres",
    tags=["chambres"],
)


@router.get("/{service_id}", response_model=ChambreAvailable)
async def get_available_room(
    service_id: int,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
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


@router.post(
    "/{service_id}/reserver", status_code=201, response_model=ReservationResponse
)
async def reserver_chambre(
    service_id: int,
    data: Annotated[CreateReservation, Body()],
    payload: Annotated[InternalPayload, Depends(check_authorization)],
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
        db=db, service_id=service_id, reservation_data=data
    )


@router.put("/{chambre_id}", response_model=SuccessWithMessage)
async def update_chambre_status(
    chambre_id: int,
    # payload: Annotated[InternalPayload, Depends(check_authorization)],
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    chambre = await service_chambre.update_chambre_status(db, chambre_id, Status.LIBRE)
    return {
        "success": True,
        "message": "Chambre mise à jour",
        "service_id": chambre.service_id,
    }


@router.delete(
    "/{reservation_id}/close",
    status_code=200,
    response_model=SuccessWithMessage,
)
async def close_reservation(
    reservation_id: int,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    """
    Clôture une réservation lors de la sortie d'un patient.
    Supprime la réservation et met la chambre en statut NETTOYAGE.
    """
    return await service_chambre.close_reservation(
        db=db,
        reservation_id=reservation_id,
    )


@router.delete(
    "/{reservation_id}/cancel",
    status_code=200,
    response_model=SuccessWithMessage,
)
async def cancel_reservation(
    # payload: Annotated[InternalPayload, Depends(check_authorization)],
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
    )
