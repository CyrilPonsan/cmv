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


class SearchPatientsParams(BaseModel):
    search: str | None = Field(default=None)
    page: int | None = Field(default=1, ge=1)
    limit: int | None = Field(default=10, ge=1, le=50)
    field: str | None = Field(default="nom")
    order: str | None = Field(default="asc")

    @field_validator("search")
    def validate_search(cls, value):
        if value and not re.match(generic_pattern, value):
            raise ValueError(
                "La propriété 'search' contient des caractères non autorisés."
            )
        return value
