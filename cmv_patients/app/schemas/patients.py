from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from .regular_expression import generic_pattern


# Modèle retourné pour l'affichage de la liste des patients dans un tableau
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


class ReadAllPatients(BaseModel):
    patients: list[PatientListItem]
    total: int
