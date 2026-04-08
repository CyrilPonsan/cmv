# Import des dépendances SQLAlchemy nécessaires
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import des variables d'environnement
from .config import DATABASE_URL, ENVIRONMENT

# Configuration de la base de données
if ENVIRONMENT == "test":
    # En environnement de test, utilise une base SQLite en mémoire
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # En production, vérifie que l'URL de la base est définie
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL must be set")
    engine = create_engine(DATABASE_URL)

# Création de la factory de sessions de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création de la classe de base pour les modèles SQLAlchemy
Base = declarative_base()
# Récupération des métadonnées de la base
metadata = Base.metadata
