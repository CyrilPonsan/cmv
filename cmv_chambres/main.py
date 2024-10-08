from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .dependancies.db_session import get_db
from .sql import models
from .settings.database import engine
from .utils.logging_setup import LoggerSetup


# Initialisation de la bdd
models.Base.metadata.create_all(bind=engine)

# Mise en place des logs
logger = LoggerSetup()

app = FastAPI()


# Politiques CORS
origins = [
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/fixtures")
def fixtures(db: Session = Depends(get_db)):
    pass
