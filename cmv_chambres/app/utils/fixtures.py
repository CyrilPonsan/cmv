# Génère des services hospitaliers composés chacun d'une quinzaine de chambres

from datetime import datetime
from sqlalchemy.orm import Session

from app.sql.models import Chambre, Service, Status

services = [
    "Urgences",
    "Chirurgie orthopédique",
    "Chirurgie vasculaire",
    "Chirurgie urologique",
    "Chirurgie plastique et esthétique",
    "Gynécologie-obstétrique",
    "Cardiologie",
    "Pneumologie",
    "Gastro-entérologie",
    "Neurologie",
    "Ophtalmologie",
    "Anesthésie-réanimation",
    "Soins intensifs",
    "Oncologie",
    "Psychiatrie",
    "Imagerie médicale (IRM, scanner, échographie, etc.)",
]


def create_fixtures(db: Session):
    print("FIXTURING ...")
    db_services: list[Service] = []
    index = -1
    for service in services:
        index += 1
        chambres = [
            Chambre(
                nom=f"{index}{'0' + str(i + 1) if i < 10 else i}",
                status=Status.LIBRE,
                dernier_nettoyage=datetime.now(),
            )
            for i in range(15)
        ]
        service = Service(nom=service, chambres=chambres)
        db_services.append(service)
    print(len(db_services))
    db.add_all(db_services)
    db.commit()
    return {"message": "Fixtures created"}
