from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv
from faker import Faker

# Import des modèles nécessaires
from app.sql.models import Base, Patient

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "PATIENTS_DATABASE_URL",
    "postgresql://postgres:cmv_patients@localhost:6003/cmv_patients",
)

# Configuration de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Liste des patients (reprise du fichier original)
objects = [
    {"first_name": "ana", "last_name": "gilbert"},
    # ... Copier la liste complète des objects depuis le fichier original ...
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
    """Crée les fixtures pour les patients"""
    print("Création des fixtures pour les patients...")

    # Création des patients à partir de la liste objects
    patients: list[Patient] = []
    for o in objects:
        patient = Patient(
            civilite="AUTRE",
            prenom=o["first_name"],
            nom=o["last_name"],
            adresse="2 rue des écrivains",
            code_postal="64000",
            ville="gelos",
            telephone="06.66.69.96.99",
            date_de_naissance=datetime(year=1969, month=7, day=20),
        )
        patients.append(patient)

    # Ajout de patients supplémentaires avec Faker
    fake = Faker("fr_FR")
    for _ in range(50):  # Ajout de 50 patients supplémentaires
        patient = Patient(
            civilite="AUTRE",
            prenom=fake.first_name().lower(),
            nom=fake.last_name().lower(),
            adresse=fake.street_address(),
            code_postal=fake.postcode(),
            ville=fake.city(),
            telephone=fake.phone_number(),
            date_de_naissance=fake.date_of_birth(minimum_age=18, maximum_age=90),
        )
        patients.append(patient)

    # Sauvegarde en base de données
    db.add_all(patients)
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
