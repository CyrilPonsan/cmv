# Import des modules nécessaires
import os

from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Clé secrète pour le chiffrement/déchiffrement
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithme utilisé pour le chiffrement
ALGORITHM = os.getenv("ALGORITHM")
