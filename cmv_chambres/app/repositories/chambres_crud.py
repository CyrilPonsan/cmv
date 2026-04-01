from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.reservation import CreateReservation, ReservationResponse
from app.sql.models import Chambre, Reservation, Status


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

    async def get_reservation_by_id(
        self, db: Session, reservation_id: int
    ) -> Reservation | None:
        return (
            db.query(Reservation)
            .filter(Reservation.id_reservation == reservation_id)
            .first()
        )

    async def cancel_reservation(self, db: Session, reservation_id: int) -> Reservation:
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

    async def get_reservations(self, db: Session, patient_id: int) -> list[Reservation]:
        return db.query(Reservation).filter(Reservation.ref == patient_id).all()

    async def create_reservation(
        self, db: Session, chambre: Chambre, reservation: CreateReservation
    ) -> ReservationResponse:
        new_reservation = Reservation(
            chambre_id=chambre.id_chambre,
            ref=reservation.patient_id,
            entree_prevue=reservation.entree_prevue,
            sortie_prevue=reservation.sortie_prevue,
        )
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        return ReservationResponse(
            reservation_id=new_reservation.id_reservation,
            chambre_id=chambre.id_chambre,
        )
