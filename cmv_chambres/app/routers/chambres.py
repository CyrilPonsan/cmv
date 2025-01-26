from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.sql.models import Chambre, Status

router = APIRouter(
    prefix="/chambres",
    tags=["chambres"],
)


@router.get("/chambres")
async def get_available_room(
    service_id: int,
    db: Session = Depends(get_db),
):
    chambre = (
        db.query(Chambre)
        .filter(Chambre.service_id == service_id, Chambre.status == Status.LIBRE)
        .first()
    )
    if not chambre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no_room_available",
        )
    return chambre
