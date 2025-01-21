from datetime import datetime
import enum

from sqlalchemy import Enum, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..utils.database import Base


class Status(enum.Enum):
    LIBRE = "libre"
    OCCUPEE = "occupée"
    NETTOYAGE = "en cours de nettoyage"


class Service(Base):
    __tablename__ = "service"

    id_service: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String, nullable=False)

    # Relation Many to one entre les entités Chambre et Service
    chambres: Mapped[list["Chambre"]] = relationship(
        "Chambre", back_populates="service", order_by="Chambre.nom"
    )


class Chambre(Base):
    __tablename__ = "chambre"

    id_chambre: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    dernier_nettoyage: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relation One to many entre les entités Service et Chambre
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id_service", ondelete="CASCADE"), nullable=False
    )
    service: Mapped[Service] = relationship("Service", back_populates="chambres")

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="chambre"
    )


class Patient(Base):
    __tablename__ = "patient"

    id_patient: Mapped[int] = mapped_column(primary_key=True, index=True)
    ref_patient: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="patient"
    )


# Table issue de la relation many to many entre les entités Chambre et Patient
class Reservation(Base):
    __tablename__ = "reservation"

    id_reservation: Mapped[int] = mapped_column(primary_key=True, index=True)
    entree_prevue: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sortie_prevue: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id_patient", ondelete="CASCADE"), nullable=False
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="reservations")

    chambre_id: Mapped[int] = mapped_column(
        ForeignKey("chambre.id_chambre", ondelete="CASCADE"), nullable=False
    )
    chambre: Mapped["Chambre"] = relationship("Chambre", back_populates="reservations")
