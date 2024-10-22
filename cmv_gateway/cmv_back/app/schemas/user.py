import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from fastapi import HTTPException, status

from .regular_expression import password_pattern


class UserBase(BaseModel):
    username: EmailStr
    password: str
    prenom: str
    nom: str
    service: str


class Role(BaseModel):
    id: int
    name: str
    label: str

    class Config:
        from_attributes = True


class User(UserBase):
    id_user: int
    role: Role

    class Config:
        from_attributes = True


# Ce schéma valide les identifiants envoyés par l'utilisateur via le formulaire de connexion
class Credentials(BaseModel):
    username: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not re.match(password_pattern, value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects.",
            )
        return value


class InternalPayload(BaseModel):
    user_id: int
    role: str
    exp: datetime
    source: str
