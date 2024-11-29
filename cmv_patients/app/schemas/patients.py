from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.sql.models import Civilite, DocumentType

from .regular_expression import generic_pattern


# Modèle utilisé pour l'affichage de la liste des patients dans un tableau
class PatientListItem(BaseModel):
    # Identifiant unique du patient
    id_patient: int
    # Civilité du patient (M., Mme, etc.)
    civilite: str
    # Prénom du patient
    prenom: str
    # Nom de famille du patient
    nom: str
    # Date de naissance du patient
    date_de_naissance: datetime
    # Numéro de téléphone du patient
    telephone: str
    # Adresse email du patient (optionnelle)
    email: EmailStr | None = Field(default=None)

    @field_validator(
        "civilite",
        "nom",
        "prenom",
        "telephone",
    )
    def validate_generic_patterns(cls, value, field):
        # Validation des champs texte avec une expression régulière générique
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value

    class Config:
        from_attributes = True


# Modèle utilisé pour retourner une liste de patients avec le nombre total de patients
class ReadAllPatients(BaseModel):
    # Liste des patients
    data: list[PatientListItem]
    # Nombre total de patients
    total: int


# Modèle utilisé pour les paramètres de pagination et de tri
class PatientsParams(BaseModel):
    # Numéro de la page (commence à 1)
    page: int = Field(default=1, ge=1)
    # Nombre d'éléments par page
    limit: int = Field(default=10, ge=1)
    # Champ utilisé pour le tri
    field: str = Field(default="nom")
    # Ordre du tri (asc ou desc)
    order: str = Field(default="asc")

    @field_validator("field")
    def validate_field(cls, value):
        # Validation des champs de tri autorisés
        if value not in ["nom", "prenom", "date_de_naissance", "email"]:
            raise ValueError(
                "La propriété 'field' doit être 'nom', 'prenom', 'date_de_naissance' ou 'email'."
            )
        return value


# Modèle utilisé pour les paramètres de recherche
class SearchPatientsParams(PatientsParams):
    # Terme de recherche
    search: str

    @field_validator("search")
    def validate_search(cls, value):
        # Validation du terme de recherche avec l'expression régulière générique
        if value and not re.match(generic_pattern, value):
            raise ValueError(
                "La propriété 'search' contient des caractères non autorisés."
            )
        return value


# Modèle utilisé pour retourner un document dans la liste des documents d'un patient
class DocumentsListItem(BaseModel):
    # Identifiant unique du document
    id_document: int
    # Nom du fichier
    nom_fichier: str
    # Type de document (enum DocumentType)
    type_document: DocumentType
    # Date de création du document
    created_at: datetime

    class Config:
        from_attributes = True


# Modèle utilisé pour la création d'un nouveau patient
class CreatePatient(BaseModel):
    # Civilité du patient
    civilite: Civilite
    # Prénom du patient
    prenom: str
    # Nom de famille du patient
    nom: str
    # Date de naissance du patient
    date_de_naissance: datetime
    # Adresse postale du patient
    adresse: str
    # Code postal du patient
    code_postal: str
    # Ville du patient
    ville: str
    # Numéro de téléphone du patient
    telephone: str
    # Adresse email du patient (optionnelle)
    email: EmailStr | None = Field(default=None)

    @field_validator("nom", "prenom", "telephone", "adresse", "code_postal", "ville")
    def validate_generic_patterns(cls, value, field):
        # Validation des champs texte avec une expression régulière générique
        if not re.match(generic_pattern, value):
            raise ValueError(
                f"La propriété '{field.field_name}' contient des caractères non autorisés."
            )
        return value


# Modèle utilisé pour retourner les informations détaillées d'un patient
class DetailPatient(CreatePatient):
    # Identifiant unique du patient
    id_patient: int
    # Liste des documents associés au patient
    documents: list[DocumentsListItem]

    class Config:
        from_attributes = True


# Modèle utilisé pour la création/modification d'un document
class DocumentData(BaseModel):
    # Type de document (enum DocumentType)
    type_document: DocumentType


class PostPatient(BaseModel):
    data: CreatePatient
