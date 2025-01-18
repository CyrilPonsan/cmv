from pydantic import BaseModel


class Chambre(BaseModel):
    id_chambre: int
    numero: int
    etat: str
    service_id: int

    class Config:
        from_attributes = True


class ServicesListItem(BaseModel):
    id_service: int
    nom: str
    chambres: list[Chambre]

    class Config:
        from_attributes = True
