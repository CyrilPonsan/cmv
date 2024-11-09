from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from .regular_expression import generic_pattern


# Modèle utilisé pour l'affichage de la liste des patients dans un tableau
class PatientListItem(BaseModel):
    id_patient: int
    civilite: str
    prenom: str
    nom: str
    date_de_naissance: datetime
    telephone: str
    email: EmailStr | None = Field(default=None)

    @field_validator(
        "civilite",
        "nom",
        "prenom",
        "telephone",
    )
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value

    class Config:
        from_attributes = True


# Modèle utilisé pour retourner une liste de patients avec le nombre total de patients
class ReadAllPatients(BaseModel):
    data: list[PatientListItem]
    total: int


# Modèle utilisé pour les paramètres de pagination et de tri
class PatientsParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    field: str = Field(default="nom")
    order: str = Field(default="asc")

    @field_validator("field")
    def validate_field(cls, value):
        if value not in ["nom", "prenom", "date_de_naissance", "email"]:
            raise ValueError(
                "La propriété 'field' doit être 'nom', 'prenom', 'date_de_naissance' ou 'email'."
            )
        return value


# Modèle utilisé pour les paramètres de recherche
class SearchPatientsParams(PatientsParams):
    search: str

    @field_validator("search")
    def validate_search(cls, value):
        if value and not re.match(generic_pattern, value):
            raise ValueError(
                "La propriété 'search' contient des caractères non autorisés."
            )
        return value


class DocumentsListItem(BaseModel):
    id_document: int
    nom_fichier: str
    type_document: str
    created_at: datetime


# Modèle utilisé pour retourner les informations d'un patient
class DetailPatient(BaseModel):
    id_patient: int
    civilite: str
    prenom: str
    nom: str
    date_de_naissance: datetime
    adresse: str
    code_postal: str
    ville: str
    telephone: str
    email: EmailStr | None = Field(default=None)
    documents: list[DocumentsListItem]

    @field_validator(
        "civilite", "nom", "prenom", "telephone", "adresse", "code_postal", "ville"
    )
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value

    class Config:
        from_attributes = True
