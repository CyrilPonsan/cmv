# Import des gestionnaires d'exceptions FastAPI
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.exceptions import ExceptionHandlerMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

from .dependancies.db_session import get_db
from .routers import api
from .sql import models
from .utils.config import ENVIRONMENT, VALKEY_HOST
from .utils.database import engine
from .utils.logging_setup import LoggerSetup
from .utils.rate_limiter import close_rate_limiter, init_rate_limiter
from app.utils.config import ENVIRONMENT


# Les migrations sont gérées par alembic
if ENVIRONMENT != "production":
    models.Base.metadata.create_all(bind=engine)

# Initialisation du logger
logger = LoggerSetup()


print(f"VALKEY_HOST: {VALKEY_HOST}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application.

    Initialise le rate limiter au démarrage et le ferme à l'arrêt.
    """
    await init_rate_limiter()
    yield
    await close_rate_limiter()


# Création de l'application FastAPI
app = FastAPI(
    root_path="",  # Set to your proxy path if needed, e.g., "/api"
    lifespan=lifespan,
)

# Inclusion des routes de l'API
app.include_router(api.router)

# Configuration CORS - Liste des origines autorisées
origins = [
    "http://localhost:5173",
    "https://clinique-montvert.fr",  # Add your domain
    "http://clinique-montvert.fr",  # Add HTTP version too
]

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
