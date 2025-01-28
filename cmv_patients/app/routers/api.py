# Import du routeur FastAPI
from fastapi import APIRouter

# Import des différents sous-routeurs de l'application
from app.routers import documents
from app.routers import patients
from app.routers import admission

# Création du routeur principal avec préfixe /api
router = APIRouter(prefix="/api", tags=["api"])

# Inclusion des sous-routeurs pour les différentes fonctionnalités
router.include_router(admission.router)  # Gestion des admissions
router.include_router(documents.router)  # Gestion des documents
router.include_router(patients.router)  # Gestion des patients
