# Import du module FastAPI pour la gestion des routes
from fastapi import APIRouter

# Import des sous-routeurs pour les services et les chambres
from app.routers import services
from app.routers import chambres

# Création du routeur principal avec le préfixe /api
router = APIRouter(prefix="/api", tags=["api"])

# Inclusion des sous-routeurs pour les services et les chambres
router.include_router(services.router)
router.include_router(chambres.router)
