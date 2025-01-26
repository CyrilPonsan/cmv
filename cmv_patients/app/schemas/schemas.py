import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr

from .regular_expression import generic_pattern


class Service(BaseModel):
    id: int
    nom: str


class Chambre(BaseModel):
    id: int
    numero: str
    status: str
    service: Service

    class Config:
        from_attributes = True


class Admission(BaseModel):
    ref_chambre: int = Field(
        description="L'identifiant de la chambre dans la bdd de l'API Chambres"
    )
    date_entree: datetime = Field(
        description="Date du début de l'hospitalisation du patient"
    )
    date_sortie: datetime = Field(description="Date de sortie du patient")


class CreateAdmission(BaseModel):
    patient_id: int
    ambulatoire: bool
    entree_le: datetime
    sortie_prevue_le: datetime
    service_id: int | None = Field(default=None)  # Optionnel si ambulatoire = True


class PaginatedRooms(BaseModel):
    total_pages: int
    rooms: list[Chambre]


class Patient(BaseModel):
    civilite: str = Field(description="Le titre du patient", max_length=255)
    prenom: str = Field(description="Le prénom du patient", max_length=255)
    nom: str = Field(description="Le nom du patient", max_length=255)
    date_naissance: datetime = Field(description="La date de naissance du patient")
    email: EmailStr | None = Field(description="Adresse email du patient", default=None)
    telephone: str = Field(description="Le numéro de téléphone du patient")

    @field_validator("civilite", "prenom", "nom", "telephone")
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value


class PatientCreate(Patient):
    adresse: str = Field(description="L'adresse du patient")
    code_postal: str = Field(
        description="Le code postal de la ville où réside le patient"
    )
    ville: str = Field(description="La ville où réside le patient")
    admission: datetime = Field(
        description="La date à laquelle le patient est a été hospitalisé"
    )
    sorti_le: datetime = Field(
        description="La date à laquelle le patient est sorti de la clinique, date à laquelle sa chambre est libérée"
    )
    sortie_prevue_le: datetime = Field(
        description="La date à laquelle on espère que la chambre soit libérée"
    )
    chambre: Chambre | None = Field(
        default=None, description="La chambre occupée ou réservée par le patient"
    )

    @field_validator(
        "adresse",
        "code_postal",
        "ville",
    )
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value


class PatientItem(Patient):
    id: int = Field(description="Identifiant du patient dans la base de données")

    class Config:
        from_attributes = True


class PatientDetail(PatientCreate):
    id: int = Field(description="Identifiant du patient dans la base de données")
    chambre: Chambre | None = Field(
        description="Entité Chambre dans la bdd, chambre affectée au patient",
        default=None,
    )
    admissions: list[Admission] | None = Field(
        description="Liste des admissions du patient",
        default=None,
    )

    class Config:
        from_attributes = True


class SuccessWithMessage(BaseModel):
    success: bool
    message: str
