from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("CHAMBRES_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
