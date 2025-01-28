# Import des modules nécessaires
from datetime import datetime
from pydantic import BaseModel


# Modèle Pydantic pour représenter un patient
class Patient(BaseModel):
    id_patient: int  # Identifiant unique du patient
    full_name: str  # Nom complet du patient


# Modèle Pydantic pour la création d'une réservation
class CreateReservation(BaseModel):
    patient: Patient  # Informations du patient
    entree_prevue: datetime  # Date et heure prévues d'entrée
    sortie_prevue: datetime  # Date et heure prévues de sortie


# Modèle Pydantic pour la réponse d'une réservation
class ReservationResponse(BaseModel):
    id_chambre: int  # Identifiant de la chambre
    nom: str  # Nom de la chambre
    status: str  # Statut actuel de la chambre
    dernier_nettoyage: datetime  # Date et heure du dernier nettoyage
    service_id: int  # Identifiant du service
    reservation_id: int  # Identifiant de la réservation
