from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..sql.models import Chambre


def get_chambres(db: Session):
    return db.query(Chambre).all()


def get_chambre_detail(db: Session, chambre_id: int):
    chambre = db.query(Chambre).filter(Chambre.id == chambre_id).first()
    if not chambre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La chambre n'existe pas.",
        )
    return chambre
