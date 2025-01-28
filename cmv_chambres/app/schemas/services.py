from datetime import datetime

from pydantic import BaseModel, Field


# Modèle Pydantic pour représenter un patient
class Patient(BaseModel):
    id_patient: int  # Identifiant unique du patient
    ref_patient: int  # Référence externe du patient
    full_name: str  # Nom complet du patient

    class Config:
        from_attributes = True  # Permet la conversion depuis les attributs SQLAlchemy


# Modèle Pydantic pour représenter une réservation
class Reservation(BaseModel):
    id_reservation: int  # Identifiant unique de la réservation
    patient: Patient  # Patient associé à la réservation
    entree_prevue: datetime  # Date et heure prévues d'entrée
    sortie_prevue: datetime  # Date et heure prévues de sortie

    class Config:
        from_attributes = True


# Modèle Pydantic pour représenter une chambre disponible
class ChambreAvailable(BaseModel):
    id_chambre: int  # Identifiant unique de la chambre
    nom: str  # Nom de la chambre
    status: str  # Statut de la chambre (libre, occupée, etc.)
    dernier_nettoyage: datetime  # Date et heure du dernier nettoyage
    service_id: int  # Identifiant du service auquel appartient la chambre

    class Config:
        from_attributes = True


# Modèle Pydantic pour représenter une chambre avec ses réservations
class Chambre(ChambreAvailable):
    reservations: list[Reservation] = Field(
        default_factory=list
    )  # Liste des réservations associées


# Modèle Pydantic pour représenter un élément de la liste des services
class ServicesListItem(BaseModel):
    id_service: int  # Identifiant unique du service
    nom: str  # Nom du service
    chambres: list[Chambre]  # Liste des chambres du service

    class Config:
        from_attributes = True
