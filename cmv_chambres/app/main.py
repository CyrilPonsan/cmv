from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError

from app.routers import api
from app.dependancies.db_session import get_db
from app.sql import models
from cmv_chambres.app.utils.database import engine
from app.utils.logging_setup import LoggerSetup


# Initialisation de la bdd
models.Base.metadata.create_all(bind=engine)

# Mise en place des logs
logger = LoggerSetup()

app = FastAPI()

app.include_router(api.router)


# Politiques CORS
origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# handle app raised http exceptions
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG an HTTP error! {repr(exc)}")
    if exc.status_code != 429:
        logger.write_log(exc.detail, request)
    return await http_exception_handler(request, exc)


# handle validation exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    logger.write_valid(request, exc)
    return await request_validation_exception_handler(request, exc)


@app.get("/fixtures")
def fixtures(db: Session = Depends(get_db)):
    pass
