from datetime import datetime
import enum

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    DateTime,
    Enum,
    func,
    Integer,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..utils.database import Base


class Civilite(enum.Enum):
    """Enumération des civilités possibles pour un patient."""

    MONSIEUR = "Monsieur"
    MADAME = "Madame"
    AUTRE = "Autre"


class DocumentType(enum.Enum):
    """Enumération des différents types de documents pouvant être associés à un patient."""

    HEALTH_INSURANCE_CARD_CERTIFICATE = (
        "health_insurance_card_certificate"  # Attestation carte vitale
    )
    AUTHORIZATION_FOR_CARE = "authorization_for_care"  # Autorisation de soins
    AUTHORIZATION_FOR_TREATMENT = (
        "authorization_for_treatment"  # Autorisation de traitement
    )
    AUTHORIZATION_FOR_VISIT = "authorization_for_visit"  # Autorisation de visite
    AUTHORIZATION_FOR_OVERNIGHT_STAY = (
        "authorization_for_overnight_stay"  # Autorisation de nuitée
    )
    AUTHORIZATION_FOR_DEPARTURE = (
        "authorization_for_departure"  # Autorisation de sortie
    )
    AUTHORIZATION_FOR_DISCONNECTION = (
        "authorization_for_disconnection"  # Autorisation de débranchement
    )
    MISCELLANEOUS = "miscellaneous"  # Divers


class Admission(Base):
    """Modèle représentant une admission d'un patient dans l'établissement."""

    __tablename__ = "admission"

    id_admission: Mapped[int] = mapped_column(primary_key=True, index=True)
    entree_le: Mapped[datetime] = mapped_column(DateTime)  # Date et heure d'entrée
    ambulatoire: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # Type d'admission (ambulatoire ou hospitalisation)
    sorti_le: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )  # Date et heure de sortie effective
    sortie_prevue_le: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )  # Date et heure de sortie prévue
    ref_chambre: Mapped[int] = mapped_column(
        Integer, nullable=True
    )  # Référence de la chambre attribuée
    ref_reservation: Mapped[int] = mapped_column(
        Integer, nullable=True
    )  # Référence de la réservation
    nom_chambre: Mapped[str] = mapped_column(
        String, nullable=True
    )  # Nom de la chambre attribuée
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )  # Date de création
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now()
    )  # Date de dernière modification

    # Relation one to many avec l'entité "Patient"
    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.id_patient",
            ondelete="CASCADE",
        )
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="admissions")


class Document(Base):
    """Modèle représentant un document associé à un patient."""

    __tablename__ = "document"

    id_document: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom_fichier: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )  # Nom unique du fichier
    type_document: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.MISCELLANEOUS, nullable=False
    )  # Type de document
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(), server_default=func.now()
    )  # Date de création

    # Relation one to many avec l'entité "Patient"
    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.id_patient",
            ondelete="CASCADE",
        )
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="documents")


class Patient(Base):
    """Modèle représentant un patient dans le système."""

    __tablename__ = "patient"

    id_patient: Mapped[int] = mapped_column(primary_key=True, index=True)
    civilite: Mapped[Civilite] = mapped_column(
        Enum(Civilite), default=Civilite.AUTRE, nullable=False
    )  # Civilité du patient
    nom: Mapped[str] = mapped_column(String, index=True)  # Nom de famille
    prenom: Mapped[str] = mapped_column(String, index=True)  # Prénom
    date_de_naissance: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False
    )  # Date de naissance
    adresse: Mapped[str] = mapped_column(String, nullable=False)  # Adresse postale
    code_postal: Mapped[str] = mapped_column(String, nullable=False)  # Code postal
    ville: Mapped[str] = mapped_column(String, nullable=False)  # Ville
    telephone: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Numéro de téléphone
    email: Mapped[str] = mapped_column(
        String, nullable=True
    )  # Adresse email (optionnelle)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )  # Date de création
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now()
    )  # Date de dernière modification

    # Relation many to one avec l'entité "Document"
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="patient"
    )
    admissions: Mapped[list["Admission"]] = relationship(
        "Admission", back_populates="patient"
    )
