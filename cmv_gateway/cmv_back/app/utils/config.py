# Import des modules nécessaires
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# URL de connexion à la base de données
DATABASE_URL = os.getenv("GATEWAY_DATABASE_URL")

# Clé secrète pour la génération des tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithme utilisé pour le chiffrement des tokens JWT
ALGORITHM = os.getenv("ALGORITHM")

# URL du service de gestion des patients
PATIENTS_SERVICE = os.getenv("PATIENTS_SERVICE")

# Durée de validité du token d'accès en minutes
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_MAX_AGE")

# Durée de validité du token de rafraîchissement en minutes
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_MAX_AGE")

# Environnement d'exécution (development, production, etc.)
ENVIRONMENT = os.getenv("ENVIRONMENT")

# URL du service de gestion des chambres
CHAMBRES_SERVICE = os.getenv("CHAMBRES_SERVICE")
