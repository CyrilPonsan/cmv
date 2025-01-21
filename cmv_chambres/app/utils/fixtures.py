# Génère des services hospitaliers composés chacun d'une quinzaine de chambres

from datetime import datetime
from sqlalchemy.orm import Session

from app.sql.models import Chambre, Service, Status

services = [
    "Anesthésie-réanimation",
    "Cardiologie",
    "Chirurgie orthopédique",
    "Chirurgie plastique et esthétique",
    "Chirurgie urologique",
    "Chirurgie vasculaire",
    "Gastro-entérologie",
    "Gynécologie-obstétrique",
    "Neurologie",
    "Oncologie",
    "Ophtalmologie",
    "Pneumologie",
    "Psychiatrie",
    "Soins intensifs",
    "Urgences",
]


def create_fixtures(db: Session):
    print("FIXTURING ...")
    db_services: list[Service] = []
    index = 0
    for service in services:
        chambres: list[Chambre] = []
        for i in range(1, 11):
            chambre = Chambre(
                nom=f"{index}{'0' + str(i) if i < 10 else i}",
                status=Status.LIBRE,
                dernier_nettoyage=datetime.now(),
            )
            chambres.append(chambre)
        service = Service(nom=service, chambres=chambres)
        db_services.append(service)
        index += 1
    print(len(db_services))
    db.add_all(db_services)
    db.commit()
    return {"message": "Fixtures created"}
