from datetime import datetime

from pydantic import BaseModel, Field


# Modèle Pydantic pour représenter un patient
class Patient(BaseModel):
    """
    Schéma représentant un patient dans le système.
    Contient les informations de base d'identification du patient.
    """

    id_patient: int  # Identifiant unique du patient
    ref_patient: int  # Référence externe du patient
    full_name: str  # Nom complet du patient

    class Config:
        from_attributes = True  # Permet la conversion depuis les attributs SQLAlchemy


# Modèle Pydantic pour représenter une réservation
class Reservation(BaseModel):
    """
    Schéma représentant une réservation de chambre.
    Associe un patient à une période de séjour dans une chambre.
    """

    id_reservation: int  # Identifiant unique de la réservation
    patient: Patient  # Patient associé à la réservation
    entree_prevue: datetime  # Date et heure prévues d'entrée
    sortie_prevue: datetime  # Date et heure prévues de sortie

    class Config:
        from_attributes = True


# Modèle Pydantic pour représenter une chambre disponible
class ChambreAvailable(BaseModel):
    """
    Schéma représentant une chambre avec ses informations de base.
    Utilisé pour afficher les chambres disponibles.
    """

    id_chambre: int  # Identifiant unique de la chambre
    nom: str  # Nom de la chambre
    status: str  # Statut de la chambre (libre, occupée, etc.)
    dernier_nettoyage: datetime  # Date et heure du dernier nettoyage
    service_id: int  # Identifiant du service auquel appartient la chambre

    class Config:
        from_attributes = True


# Modèle Pydantic pour représenter une chambre avec ses réservations
class Chambre(ChambreAvailable):
    """
    Extension du schéma ChambreAvailable incluant les réservations associées.
    Utilisé pour une vue complète d'une chambre avec son planning.
    """

    reservations: list[Reservation] = Field(
        default_factory=list
    )  # Liste des réservations associées


class ServicesList(BaseModel):
    """
    Schéma de base pour représenter un service hospitalier.
    Contient les informations minimales d'un service.
    """

    id_service: int  # Identifiant unique du service
    nom: str  # Nom du service

    class Config:
        from_attributes = True


# Modèle Pydantic pour représenter un élément de la liste des services
class ServicesListItem(ServicesList):
    """
    Extension du schéma ServicesList incluant la liste des chambres.
    Utilisé pour afficher un service avec toutes ses chambres.
    """

    chambres: list[Chambre]  # Liste des chambres du service
