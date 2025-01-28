# Import des gestionnaires d'exceptions FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

# Import des composants FastAPI nécessaires
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import des routes de l'API
from .routers import api

# Import des utilitaires
from .utils.logging_setup import LoggerSetup
from .utils.database import engine
from .sql import models


# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

# Initialisation du logger
logger = LoggerSetup()

# Création de l'application FastAPI
app = FastAPI()

# Inclusion des routes de l'API
app.include_router(api.router)

# Configuration des politiques CORS (Cross-Origin Resource Sharing)
origins = []

# Ajout du middleware CORS à l'application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Liste des origines autorisées
    allow_credentials=True,  # Autorise l'envoi des cookies
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP
    allow_headers=["*"],  # Autorise tous les headers HTTP
)


# Gestionnaire personnalisé pour les exceptions HTTP levées par l'application
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    # Log de l'erreur pour debug
    print(f"OMG an HTTP error! {repr(exc)}")
    # Si ce n'est pas une erreur de rate limiting (429), on log l'erreur
    if exc.status_code != 429:
        logger.write_log(exc.detail, request)
    # Utilisation du gestionnaire d'exceptions HTTP par défaut
    return await http_exception_handler(request, exc)


# Gestionnaire pour les erreurs de validation des données reçues
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Log de l'erreur pour debug
    print(f"OMG! The client sent invalid data!: {exc}")
    # Enregistrement de l'erreur de validation dans les logs
    logger.write_valid(request, exc)
    # Utilisation du gestionnaire d'erreurs de validation par défaut
    return await request_validation_exception_handler(request, exc)
