from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("GATEWAY_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
PATIENTS_SERVICE = os.getenv("PATIENTS_SERVICE")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_MAX_AGE")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_MAX_AGE")
ENVIRONMENT = os.getenv("ENVIRONMENT")
