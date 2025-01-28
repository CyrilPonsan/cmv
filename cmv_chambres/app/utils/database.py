# Import des modules nécessaires de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import de l'URL de connexion à la base de données depuis la configuration
from .config import DATABASE_URL

# Création du moteur SQLAlchemy si l'URL de la base de données est définie
if DATABASE_URL:
    # Initialisation du moteur avec l'URL de connexion
    engine = create_engine(DATABASE_URL)

    # Configuration de la factory de sessions
    # autocommit=False : Les transactions doivent être explicitement committées
    # autoflush=False : Les modifications ne sont pas automatiquement synchronisées avec la BD
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Création de la classe de base pour les modèles SQLAlchemy
    Base = declarative_base()
    # Récupération des métadonnées de la base
    metadata = Base.metadata
