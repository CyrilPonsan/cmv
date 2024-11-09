from datetime import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
    DateTime,
    Enum,
    Table,
    func,
    Integer,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..utils.database import Base


class Civilite(enum.Enum):
    MONSIEUR = "Monsieur"
    MADAME = "Madame"
    AUTRE = "Autre"
    ROBERTO = "Roberto"


class DocumentType(enum.Enum):
    ATTESTATION_CARTE_VITALE = "Attestation de carte vitale"
    AUTORISATION_DE_SOINS = "Autorisation de soins"
    AUTORISATION_DE_TRAITEMENT = "Autorisation de traitement"
    AUTORISATION_DE_VISITE = "Autorisation de visite"
    AUTORISATION_DE_REMISE_A_NUIT = "Autorisation de remise à nuit"
    AUTORISATION_DE_DEPART = "Autorisation de départ"
    AUTORISATION_DE_DEBRANCHEMENT = "Autorisation de débranchement"
    AUTRE = "Divers"


class Admission(Base):
    __tablename__ = "admission"

    id_admission: Mapped[int] = mapped_column(primary_key=True, index=True)
    entree_le: Mapped[datetime] = mapped_column(DateTime)
    ambulatoire: Mapped[bool] = mapped_column(Boolean, default=True)
    sorti_le: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sortie_prevue_le: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ref_chambre: Mapped[int] = mapped_column(Integer, nullable=True)


class Document(Base):
    __tablename__ = "document"

    id_document: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom_fichier: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    type_document: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.AUTRE, nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    # relation one to many avec l'entité "Patient"
    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.id_patient",
            ondelete="CASCADE",
        )
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="documents")


class Patient(Base):
    __tablename__ = "patient"

    id_patient: Mapped[int] = mapped_column(primary_key=True, index=True)
    civilite: Mapped[Civilite] = mapped_column(
        Enum(Civilite), default=Civilite.AUTRE, nullable=False
    )
    nom: Mapped[str] = mapped_column(String, index=True)
    prenom: Mapped[str] = mapped_column(String, index=True)
    date_de_naissance: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    adresse: Mapped[str] = mapped_column(String, nullable=False)
    code_postal: Mapped[str] = mapped_column(String, nullable=False)
    ville: Mapped[str] = mapped_column(String, nullable=False)
    telephone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now()
    )

    # relation many to one avec l'entité "Document"
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="patient"
    )


admission_patient = Table(
    "admission_patient",
    Base.metadata,
    Column(
        "patient_id",
        ForeignKey("patient.id_patient", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "admision_id",
        ForeignKey("admission.id_admission", ondelete="CASCADE"),
        primary_key=True,
    ),
)
