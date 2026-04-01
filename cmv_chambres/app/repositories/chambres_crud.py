from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.reservation import CreateReservation
from app.sql.models import Chambre, Patient, Reservation, Status


class PgChambresRepository:
    """Repository PostgreSQL pour les opérations CRUD sur les chambres."""

    async def get_chambre_by_id(self, db: Session, chambre_id: int) -> Chambre | None:
        return db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()

    async def get_available_room(self, db: Session, service_id: int) -> Chambre | None:
        return (
            db.query(Chambre)
            .filter(Chambre.service_id == service_id, Chambre.status == Status.LIBRE)
            .first()
        )

    async def update_chambre_status(
        self, db: Session, chambre_id: int, chambre_status: Status
    ) -> Chambre:
        chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
            )
        chambre.status = chambre_status
        db.commit()
        db.refresh(chambre)
        return chambre

    async def get_patient(self, db: Session, patient_id: int) -> Patient | None:
        return db.query(Patient).filter(Patient.ref_patient == patient_id).first()

    async def create_reservation(
        self,
        db: Session,
        chambre: Chambre,
        patient: Patient,
        reservation: CreateReservation,
    ) -> Reservation:
        new_reservation = Reservation(
            patient=patient,
            chambre=chambre,
            entree_prevue=reservation.entree_prevue,
            sortie_prevue=reservation.sortie_prevue,
        )
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        return new_reservation

    async def get_reservation_by_id(
        self, db: Session, reservation_id: int
    ) -> Reservation | None:
        return (
            db.query(Reservation)
            .filter(Reservation.id_reservation == reservation_id)
            .first()
        )

    async def cancel_reservation(
        self, db: Session, reservation_id: int
    ) -> Reservation:
        reservation = (
            db.query(Reservation)
            .filter(Reservation.id_reservation == reservation_id)
            .first()
        )
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="reservation_not_found",
            )
        db.delete(reservation)
        db.commit()
        return reservation

    async def get_reservations(
        self, db: Session, patient_id: int
    ) -> list[Reservation]:
        return db.query(Reservation).filter(Reservation.patient_id == patient_id).all()
