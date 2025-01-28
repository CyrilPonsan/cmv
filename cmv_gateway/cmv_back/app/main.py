# Import des gestionnaires d'exceptions FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import des middlewares personnalisés
from app.middleware.exceptions import ExceptionHandlerMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from .routers import api
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

# Configuration CORS - Liste des origines autorisées
origins = []

# Ajout du middleware CORS avec les paramètres de sécurité
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

# Ajout des middlewares de gestion des exceptions et de sécurité
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# Gestionnaire personnalisé pour les exceptions HTTP
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG an HTTP error! {repr(exc)}")
    if exc.status_code != 429:
        logger.write_log(exc.detail, request)
    return await http_exception_handler(request, exc)


# Gestionnaire pour les erreurs de validation des requêtes
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    logger.write_valid(request, exc)
    return await request_validation_exception_handler(request, exc)


# Configuration pour servir l'application Vue en production
try:
    # Définition du répertoire de build de l'app Vue
    build_dir = Path(__file__).resolve().parent / "dist"
    index_path = build_dir / "index.html"

    # Configuration pour servir les fichiers statiques
    app.mount("/assets", StaticFiles(directory=build_dir / "assets"), name="assets")

    # Route catch-all pour l'application SPA
    @app.get("/{catchall:path}")
    async def serve_spa(catchall: str):
        # Vérification si le fichier existe, sinon retourne index.html
        path = build_dir / catchall
        if path.is_file():
            return FileResponse(path)
        return FileResponse(index_path)

except RuntimeError:
    # Message d'erreur si le répertoire de build n'existe pas
    print("No build directory found. Running in development mode.")
