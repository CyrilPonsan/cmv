from datetime import datetime

from pydantic import BaseModel


class Patient(BaseModel):
    id_patient: int
    full_name: str


class CreateReservation(BaseModel):
    patient: Patient
    entree_prevue: datetime
    sortie_prevue: datetime
