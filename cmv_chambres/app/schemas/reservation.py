# Import des modules nécessaires
from datetime import datetime

from pydantic import BaseModel


# Modèle Pydantic pour la création d'une réservation
class CreateReservation(BaseModel):
    patient_id: int  # Informations du patient
    entree_prevue: datetime  # Date et heure prévues d'entrée
    sortie_prevue: datetime  # Date et heure prévues de sortie


# Modèle Pydantic pour la réponse d'une réservation
class ReservationResponse(BaseModel):
    reservation_id: int  # Identifiant de la réservation
    chambre_id: int
    sortie_prevue_le: datetime
