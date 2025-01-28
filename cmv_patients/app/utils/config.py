from dotenv import load_dotenv
import os

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# URL de connexion à la base de données des patients
DATABASE_URL = os.getenv("PATIENTS_DATABASE_URL")
# Clé secrète pour la génération des tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")
# Algorithme utilisé pour la génération des tokens JWT
ALGORITHM = os.getenv("ALGORITHM")
# Environnement d'exécution (development, production, etc.)
ENVIRONMENT = os.getenv("ENVIRONMENT")
# Nom du bucket AWS S3 pour le stockage des documents
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
# Identifiant d'accès au compte AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# Clé secrète d'accès au compte AWS
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# Région AWS où se trouve le bucket S3
AWS_REGION = os.getenv("AWS_REGION")
# URL du service de gestion des chambres
CHAMBRES_SERVICE = os.getenv("CHAMBRES_SERVICE")
