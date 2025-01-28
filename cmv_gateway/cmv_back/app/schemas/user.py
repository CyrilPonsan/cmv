# Import des modules nécessaires
import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from fastapi import HTTPException, status

from .regular_expression import password_pattern


# Modèle de base pour les utilisateurs contenant les champs communs
class UserBase(BaseModel):
    username: EmailStr  # Email de l'utilisateur servant d'identifiant
    password: str  # Mot de passe de l'utilisateur
    prenom: str  # Prénom de l'utilisateur
    nom: str  # Nom de l'utilisateur
    service: str  # Service auquel l'utilisateur est rattaché


# Modèle pour les rôles utilisateur
class Role(BaseModel):
    id: int  # Identifiant unique du rôle
    name: str  # Nom du rôle (ex: "admin", "user")
    label: str  # Libellé du rôle pour l'affichage

    class Config:
        from_attributes = True  # Permet la conversion automatique depuis l'ORM


# Modèle complet d'utilisateur héritant du modèle de base
class User(UserBase):
    id_user: int  # Identifiant unique de l'utilisateur
    role: Role  # Rôle associé à l'utilisateur

    class Config:
        from_attributes = True  # Permet la conversion automatique depuis l'ORM


# Modèle pour la validation des identifiants de connexion
class Credentials(BaseModel):
    username: EmailStr  # Email de l'utilisateur
    password: str  # Mot de passe à valider

    @field_validator("password")
    def validate_password(cls, value):
        """
        Valide le format du mot de passe selon le pattern défini
        Lève une exception si le format est invalide
        """
        if not re.match(password_pattern, value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects.",
            )
        return value


# Modèle pour le payload du token JWT interne
class InternalPayload(BaseModel):
    user_id: int  # Identifiant de l'utilisateur
    role: str  # Rôle de l'utilisateur
    exp: datetime  # Date d'expiration du token
    source: str  # Source du token
