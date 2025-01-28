# Import du module FastAPI pour la gestion des routes
from fastapi import APIRouter

# Import des différents modules de routage
from app.routers import chambres
from . import auth, patients, users

# Création du routeur principal avec préfixe /api
router = APIRouter(prefix="/api", tags=["api"])


# Inclusion des sous-routeurs pour chaque fonctionnalité
router.include_router(auth.router)  # Routes d'authentification
router.include_router(chambres.router)  # Routes de gestion des chambres
router.include_router(patients.router)  # Routes de gestion des patients
router.include_router(users.router)  # Routes de gestion des utilisateurs
