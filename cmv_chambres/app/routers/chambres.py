from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.sql.models import Chambre, Patient, Status, Reservation
from app.schemas.reservation import CreateReservation

router = APIRouter(
    prefix="/chambres",
    tags=["chambres"],
)


@router.get("/{service_id}")
async def get_available_room(
    service_id: int,
    db: Session = Depends(get_db),
):
    print(f"CHAMBRE SAYS COUCOU {service_id}")
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
    return {
        "id_chambre": chambre.id_chambre,
        "nom": chambre.nom,
        "status": chambre.status.value,
        "dernier_nettoyage": chambre.dernier_nettoyage,
        "service_id": chambre.service_id,
    }


@router.post("/{chambre_id}/rerserver", status_code=status.HTTP_201_CREATED)
async def rerserver_chambre(
    chambre_id: int,
    data: Annotated[CreateReservation, Body()],
    db: Session = Depends(get_db),
):
    chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
    if not chambre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
        )
    exisiting_patient = (
        db.query(Patient).filter(Patient.ref_patient == data.patient.id_patient).first()
    )
    if not exisiting_patient:
        exisiting_patient = Patient(
            ref_patient=data.patient.id_patient,
            full_name=data.patient.full_name,
        )
        db.add(exisiting_patient)
        db.commit()
        db.refresh(exisiting_patient)

    chambre.status = Status.OCCUPEE
    chambre.patient = exisiting_patient
    db.commit()
    db.refresh(chambre)

    reservation = Reservation(
        patient=exisiting_patient,
        chambre=chambre,
        entree_prevue=data.entree_prevue,
        sortie_prevue=data.sortie_prevue,
    )
    db.add(reservation)
    db.commit()

    return {
        "id_chambre": chambre.id_chambre,
        "nom": chambre.nom,
        "status": chambre.status.value,
        "dernier_nettoyage": chambre.dernier_nettoyage,
        "service_id": chambre.service_id,
    }
