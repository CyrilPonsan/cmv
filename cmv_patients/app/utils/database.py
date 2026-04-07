# Import des dépendances SQLAlchemy nécessaires
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Import des variables d'environnement
from .config import DATABASE_URL, ENVIRONMENT

# Configuration de la base de données
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL must be set")
engine = create_engine(DATABASE_URL)

print(f"DATA BASE : {ENVIRONMENT} {DATABASE_URL}")

# Création de la factory de sessions de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création de la classe de base pour les modèles SQLAlchemy
class Base(DeclarativeBase):
    pass

# Récupération des métadonnées de la base
metadata = Base.metadata
