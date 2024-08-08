from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("AUTH_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
HOME_SERVICE = os.getenv("HOME_SERVICE")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_MAX_AGE")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_MAX_AGE")
