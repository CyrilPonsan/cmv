from datetime import datetime

from pydantic import BaseModel


class InternalPayload(BaseModel):
    # Identifiant unique de l'utilisateur
    user_id: int
    # Rôle de l'utilisateur (ex: admin, user, etc.)
    role: str
    # Date d'expiration du token
    exp: datetime
    # Source de la requête (ex: web, mobile, etc.)
    source: str


# Modèle pour les rôles utilisateur
class Role(BaseModel):
    id: int  # Identifiant unique du rôle
    name: str  # Nom du rôle (ex: "admin", "user")
    label: str  # Libellé du rôle pour l'affichage


# Modèle complet d'utilisateur héritant du modèle de base
class User(BaseModel):
    id_user: int  # Identifiant unique de l'utilisateur
    role: Role  # Rôle associé à l'utilisateur
