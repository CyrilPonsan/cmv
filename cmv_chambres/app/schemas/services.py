from datetime import datetime

from pydantic import BaseModel, Field
from pydantic import ConfigDict


# Modèle Pydantic pour représenter une réservation
class Reservation(BaseModel):
    """
    Schéma représentant une réservation de chambre.
    """
    model_config = ConfigDict(from_attributes=True)

    id_reservation: int
    ref: int  # Référence du patient
    entree_prevue: datetime
    sortie_prevue: datetime


# Modèle Pydantic pour représenter une chambre disponible
class ChambreAvailable(BaseModel):
    """
    Schéma représentant une chambre avec ses informations de base.
    Utilisé pour afficher les chambres disponibles.
    """
    model_config = ConfigDict(from_attributes=True)

    id_chambre: int  # Identifiant unique de la chambre
    nom: str  # Nom de la chambre
    status: str  # Statut de la chambre (libre, occupée, etc.)
    dernier_nettoyage: datetime  # Date et heure du dernier nettoyage
    service_id: int  # Identifiant du service auquel appartient la chambre


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
    model_config = ConfigDict(from_attributes=True)

    id_service: int  # Identifiant unique du service
    nom: str  # Nom du service


# Modèle Pydantic pour représenter un élément de la liste des services
class ServicesListItem(ServicesList):
    """
    Extension du schéma ServicesList incluant la liste des chambres.
    Utilisé pour afficher un service avec toutes ses chambres.
    """

    chambres: list[Chambre]  # Liste des chambres du service
