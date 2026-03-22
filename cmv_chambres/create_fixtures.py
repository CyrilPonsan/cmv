from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

# Import des modèles nécessaires
from app.sql.models import Base, Chambre, Service, Status

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "CHAMBRES_DATABASE_URL",
    "postgresql://postgres:cmv_chambres@localhost:6002/cmv_chambres",
)

# Configuration de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Liste des services
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


def init_db():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Crée une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_fixtures(db: Session):
    """Crée les fixtures pour les services et les chambres"""
    print("Création des fixtures pour les services et les chambres...")

    db_services: list[Service] = []
    index = 0

    for service_name in services:
        # Création des chambres pour ce service
        chambres: list[Chambre] = []
        for i in range(1, 11):  # 10 chambres par service
            chambre = Chambre(
                nom=f"{index}{'0' + str(i) if i < 10 else i}",
                status=Status.LIBRE,
                dernier_nettoyage=datetime.now(),
            )
            chambres.append(chambre)

        # Création du service avec ses chambres
        service = Service(nom=service_name, chambres=chambres)
        db_services.append(service)
        index += 1

    # Sauvegarde en base de données
    db.add_all(db_services)
    db.commit()

    return {"message": "Fixtures created successfully"}


if __name__ == "__main__":
    try:
        # Initialisation de la base de données
        init_db()

        # Création d'une session
        db = next(get_db())

        # Création des fixtures
        result = create_fixtures(db)
        print(result["message"])

    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
