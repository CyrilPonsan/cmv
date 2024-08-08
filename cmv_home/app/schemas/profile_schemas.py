import re
from pydantic import BaseModel, Field, field_validator

from .regular_expression import generic_pattern


# modèle utilisé pour l'ajout où la modification d'un profil
class Profile(BaseModel):
    username: str = Field(
        description="Le surnom de l'utilisateur",
        max_length=50,
    )
    nom: str = Field(
        description="Le nom de l'utilisateur",
        max_length=255,
    )
    prenom: str | None = Field(
        description="Le prénom de l'utilisateur",
        default=None,
        max_length=255,
    )

    # validation des champs utilisant la même expression régulière
    @field_validator("username", "nom")
    def validate_generic_patterns(cls, value, field):
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value

    # validation du champ prénom avec une expression régulière s'il est présent dans le corps de la requête
    @field_validator("prenom")
    def validate_prenom(cls, value):
        if len(value) > 0 and not re.match(generic_pattern, value):
            raise ValueError("Le prénom contient des caractères non autorisés.")
        return value
