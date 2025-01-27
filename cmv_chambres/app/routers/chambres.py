from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.schemas.reservation import CreateReservation
from app.services.chambres import get_chambres_service
from app.schemas.services import ChambreAvailable

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
    return await service_chambre.get_available_room(db=db, service_id=service_id)


@router.post("/{chambre_id}/reserver", status_code=201)
async def rerserver_chambre(
    chambre_id: int,
    data: Annotated[CreateReservation, Body()],
    service_chambre=Depends(get_chambres_service),
    db: Session = Depends(get_db),
):
    return await service_chambre.post_reservation(
        db=db, chambre_id=chambre_id, reservation_data=data
    )
