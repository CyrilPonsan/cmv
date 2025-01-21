from sqlalchemy.orm import Session
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import hashlib

from app.sql import models

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cmv_gateway")
DB_USER = os.getenv("DB_USER", "your_username")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuration du hachage de mot de passe
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

hashed_password = hash_password("Abcdef@123456")

# Configuration de l'engine SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# cuisines : 20
# entretien : 30
# accueil : 15
# docteurs : 20
# infirimières : 95
# RH : 10
# parc auto : 5
# it : 5

roles = [
    {"name": "it", "label": "Service IT"},
    {"name": "nurses", "label": "Service Infirmières"},
    {"name": "doctors", "label": "Service Médecin Chef"},
    {"name": "cleaning", "label": "Service Entretien"},
    {"name": "kitchen", "label": "Service Cuisine"},
    {"name": "hr", "label": "Service RH"},
    {"name": "vehicles", "label": "Service Parc Auto"},
    {"name": "home", "label": "Service Accueil"},
]

objects = [
    {"first_name": "ana", "last_name": "gilbert"},
    {"first_name": "katherine", "last_name": "miller"},
    {"first_name": "martin", "last_name": "lawrence"},
    {"first_name": "krystal", "last_name": "brown"},
    {"first_name": "amy", "last_name": "freeman"},
    {"first_name": "tyler", "last_name": "ramos"},
    {"first_name": "edward", "last_name": "grant"},
    {"first_name": "samuel", "last_name": "forbes"},
    {"first_name": "michael", "last_name": "freeman"},
    {"first_name": "kristi", "last_name": "boyd"},
    {"first_name": "ralph", "last_name": "avila"},
    {"first_name": "heather", "last_name": "booker"},
    {"first_name": "shane", "last_name": "edwards"},
    {"first_name": "dana", "last_name": "ruiz"},
]

usernames: list[str] = []
for object in objects:
    username = object["first_name"] + "." + object["last_name"] + "@cmv.fr"
    usernames.append(username)

def create_fixtures(db: Session):
    index = 0

    db_roles: list[models.Role] = []
    for elem in roles:
        role = models.Role(
            name=elem["name"],
            label=elem["label"],
        )
        db_roles.append(role)
    db.add_all(db_roles)
    db.commit()

    admin_role = db.query(models.Role).filter(models.Role.name == "it").first()
    nurse_role = db.query(models.Role).filter(models.Role.name == "nurses").first()
    home_role = db.query(models.Role).filter(models.Role.name == "home").first()

    permissions = [
        {"role": nurse_role, "action": "get", "resource": "chambres"},
        {"role": nurse_role, "action": "get", "resource": "services"},
        {"role": home_role, "action": "get", "resource": "patients"},
        {"role": home_role, "action": "get", "resource": "documents"},
        {"role": home_role, "action": "post", "resource": "documents"},
        {"role": home_role, "action": "delete", "resource": "documents"},
        {"role": home_role, "action": "post", "resource": "patients"},
        {"role": home_role, "action": "put", "resource": "patients"},
        {"role": home_role, "action": "delete", "resource": "patients"},
    ]

    db_perms: list[models.Permission] = []
    for perm in permissions:
        db_perm = models.Permission(
            role=perm["role"],
            action=perm["action"],
            resource=perm["resource"],
        )
        db_perms.append(db_perm)

    db.add_all(db_perms)
    db.commit()

    user = models.User(
        username="admin@cmv.fr",
        password=hashed_password,
        prenom="jacques",
        nom="durand",
        is_active=True,
        service="it",
    )

    home = models.User(
        username="accueil@cmv.fr",
        password=hashed_password,
        prenom="jacqueline",
        nom="dupond",
        is_active=True,
        service="patients",
    )

    user.role = admin_role
    home.role = home_role
    db.add(user)
    db.add(home)
    db.commit()

    users_type = [
        {"role": "it", "qty": 4},
        {"role": "vehicles", "qty": 5},
        {"role": "hr", "qty": 10},
        {"role": "kitchen", "qty": 20},
        {"role": "cleaning", "qty": 30},
        {"role": "doctors", "qty": 20},
        {"role": "nurses", "qty": 95},
        {"role": "home", "qty": 15},
    ]

    for item in users_type:
        role = db.query(models.Role).filter(models.Role.name == item["role"]).first()
        index = create_users(db, index, item["qty"], role)

    return {"message": "done"}

def create_users(db, idx, qty, role):
    db_users: list[models.User] = []
    for i in range(0, qty):
        user = models.User(
            username=usernames[idx],
            password=hashed_password,
            prenom=objects[idx]["first_name"],
            nom=objects[idx]["last_name"],
            service=role.name,
        )
        user.role = role
        db_users.append(user)
        idx += 1
    db.add_all(db_users)
    db.commit()
    return idx

def create_object():
    fake = Faker()
    object = {
        "first_name": fake.first_name().lower(),
        "last_name": fake.last_name().lower(),
    }
    return object

if __name__ == "__main__":
    # Création des tables si elles n'existent pas
    models.Base.metadata.create_all(bind=engine)
    
    # Création d'une session
    db = SessionLocal()
    
    try:
        # Création des fixtures
        result = create_fixtures(db)
        print(result["message"])
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
    finally:
        db.close()
