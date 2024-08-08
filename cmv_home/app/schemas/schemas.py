import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .regular_expression import generic_pattern


class Chambre(BaseModel):
    id: int
    numero: str
    status: str

    class Config:
        from_attributes = True


class Service(BaseModel):
    nom: str
    chambres: list[Chambre]

    class Config:
        from_attributes = True


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class PatientBase(BaseModel):
    civilite: str = Field(description="Le titre du patient", max_length=255)
    prenom: str = Field(description="Le prénom du patient", max_length=255)
    nom: str = Field(description="Le nom du patient", max_length=255)
    date_naissance: datetime = Field(description="La date de naissance du patient")
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

    @field_validator("civilite", "prenom", "nom")
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value


class Patient(PatientBase):
    id: int
    chambre: Chambre | None

    class Config:
        from_attributes = True


class ChambreWithPatient(Chambre):
    patient: Patient | None
