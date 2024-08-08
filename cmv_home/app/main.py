from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.services.fixtures import create_fixtures
from .routers import api
from app.sql import models
from app.sql.database import engine
from .logging_setup import LoggerSetup
import logging


# setup root logger
logger_setup = LoggerSetup()

# get logger for module
LOGGER = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api.router)

origins = [
    "http://localhost:5173",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" @app.on_event("startup")
async def startup():
    LOGGER.info("--- Start up App ---")

@app.on_event("shutdown")
async def shutdown():
    LOGGER.info("--- shutdown App ---") """


@app.get("/fixtures")
def fixtures(db: Session = Depends(get_db)):
    return create_fixtures(db)
