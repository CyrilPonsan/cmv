from dotenv import load_dotenv
import os

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# URL de connexion à la base de données ML
DATABASE_URL = os.getenv("ML_DATABASE_URL")
# Clé secrète pour la validation des tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")
# Algorithme utilisé pour la validation des tokens JWT
ALGORITHM = os.getenv("ALGORITHM")
# Environnement d'exécution (development, production, etc.)
ENVIRONMENT = os.getenv("ENVIRONMENT")
# Chemin vers le fichier du modèle XGBoost (.json ou .joblib)
MODEL_PATH = os.getenv("MODEL_PATH", "./models/xgboost_model.json")
# Activation de l'explicabilité SHAP (true/false)
SHAP_ENABLED = os.getenv("SHAP_ENABLED", "false").lower() == "true"
