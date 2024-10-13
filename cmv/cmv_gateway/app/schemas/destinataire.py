import re
from typing import Optional
from pydantic import BaseModel, validator
from .regular_expression import generic_pattern


class DestinataireBase(BaseModel):
    civilite: Optional[str] = None
    prenom: Optional[str] = None
    nom: str
    adresse: str
    complement: Optional[str] = None
    code_postal: str
    ville: str
    telephone: Optional[str] = None
    
    @validator("civilite")
    def validate_civilite(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("La civilité contient des caractères non autorisés.")
        if len(value) > 10:
            raise ValueError("La civilité ne doit pas avoir plus de dix caractères.")
        return value
    
    @validator("prenom")
    def validate_prenom(cls, value):
        print("hello validator")
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("Le prénom contient des caractères non autorisés.")
        if len(value) > 254:
            raise ValueError("Le prénom ne doit pas avoir plus de 255 caractères.")
        return value

    @validator("nom")
    def validate_nom(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("Le nom contient des caractères non autorisés.")
        if len(value) > 254:
            raise ValueError("Le nom ne doit pas avoir plus de 255 caractères.")
        return value
    
    @validator("adresse")
    def validate_adresse(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("L'adresse contient des caractères non autorisés.")
        if len(value) > 254:
            raise ValueError("L'adresse ne doit pas avoir plus de 255 caractères.")
        return value

    @validator("complement")
    def validate_complement(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("Le complément d'adresse contient des caractères non autorisés.")
        if len(value) > 254:
            raise ValueError("Le complément d'adresse ne doit pas avoir plus de 255 caractères.")
        return value

    @validator("code_postal")
    def validate_code_postal(cls, value):  
        print(f"value : {cls}")
        if not re.fullmatch(r'^\d{5}$', value):
            raise ValueError("Le code postal n'est pas conforme à l'expression régulière.")
        return value

    @validator("ville")
    def validate_ville(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("La ville contient des caractères non autorisés.")
        if len(value) > 254:
            raise ValueError("La ville ne doit pas avoir plus de 255 caractères.")
        return value
    
    @validator("telephone")
    def validate_telephone(cls, value):
        if not re.fullmatch(generic_pattern, value):
            raise ValueError("Le numéro de téléphone contient des caractères non autorisés.")
        if len(value) > 20:
            raise ValueError("Le numéro de téléphone ne doit pas avoir plus de 255 caractères.")
        return value


class DestinataireCreate(DestinataireBase):
    pass


class Destinataire(DestinataireBase):
    id: int

    class Config:
        from_attributes = True


class DestinataireHome(BaseModel):
    id: int
    civilite: Optional[str] 
    prenom: Optional[str] 
    nom: str
    adresse: str
    complement: Optional[str] 
    code_postal: str
    ville: str
    telephone: Optional[str]

    class Config:
        from_attributes = True
        