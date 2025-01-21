from datetime import datetime

from pydantic import BaseModel, Field


class Patient(BaseModel):
    id_patient: int
    ref_patient: int
    full_name: str

    class Config:
        from_attributes = True


class Reservation(BaseModel):
    id_reservation: int
    patient: Patient
    entree_prevue: datetime
    sortie_prevue: datetime

    class Config:
        from_attributes = True


class Chambre(BaseModel):
    id_chambre: int
    nom: str
    status: str
    dernier_nettoyage: datetime
    service_id: int
    reservations: list[Reservation] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ServicesListItem(BaseModel):
    id_service: int
    nom: str
    chambres: list[Chambre]

    class Config:
        from_attributes = True
