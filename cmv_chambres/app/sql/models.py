# Import des modules nécessaires
from datetime import datetime
import enum

from sqlalchemy import Enum, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..utils.database import Base


# Énumération des différents statuts possibles pour une chambre
class Status(enum.Enum):
    LIBRE = "libre"  # Chambre disponible
    OCCUPEE = "occupée"  # Chambre actuellement occupée
    NETTOYAGE = "en cours de nettoyage"  # Chambre en cours de nettoyage


# Modèle SQLAlchemy pour représenter un service hospitalier
class Service(Base):
    __tablename__ = "service"

    # Colonnes de la table
    id_service: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique du service
    nom: Mapped[str] = mapped_column(String, nullable=False)  # Nom du service

    # Relation Many to one entre les entités Chambre et Service
    chambres: Mapped[list["Chambre"]] = relationship(
        "Chambre", back_populates="service", order_by="Chambre.nom"
    )


# Modèle SQLAlchemy pour représenter une chambre d'hôpital
class Chambre(Base):
    __tablename__ = "chambre"

    # Colonnes de la table
    id_chambre: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique de la chambre
    nom: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )  # Nom unique de la chambre
    status: Mapped[Status] = mapped_column(
        Enum(Status), nullable=False
    )  # Statut actuel de la chambre
    dernier_nettoyage: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # Date et heure du dernier nettoyage

    # Relation One to many entre les entités Service et Chambre
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id_service", ondelete="CASCADE"), nullable=False
    )
    service: Mapped[Service] = relationship("Service", back_populates="chambres")

    # Relation avec les réservations
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="chambre"
    )


# Modèle SQLAlchemy pour représenter un patient
class Patient(Base):
    __tablename__ = "patient"

    # Colonnes de la table
    id_patient: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique du patient
    ref_patient: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True
    )  # Référence externe unique du patient
    full_name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Nom complet du patient

    # Relation avec les réservations
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="patient"
    )


# Modèle SQLAlchemy pour représenter une réservation (relation many-to-many entre Chambre et Patient)
class Reservation(Base):
    __tablename__ = "reservation"

    # Colonnes de la table
    id_reservation: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique de la réservation
    entree_prevue: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # Date et heure prévues d'entrée
    sortie_prevue: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # Date et heure prévues de sortie

    # Relation avec le patient
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id_patient", ondelete="CASCADE"), nullable=False
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="reservations")

    # Relation avec la chambre
    chambre_id: Mapped[int] = mapped_column(
        ForeignKey("chambre.id_chambre", ondelete="CASCADE"), nullable=False
    )
    chambre: Mapped["Chambre"] = relationship("Chambre", back_populates="reservations")
