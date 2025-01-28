# Import des modules nécessaires de FastAPI
from fastapi import APIRouter, Depends, Request

# Import des services et dépendances
from app.services.chambres import get_chambres_service
from app.dependancies.httpx_client import get_http_client

# Création du routeur pour les chambres avec préfixe et tag
router = APIRouter(prefix="/chambres", tags=["chambres"])


@router.get("/{path:path}")
async def read_all_chambres(
    path: str,  # Chemin de la requête
    request: Request,  # Requête HTTP entrante
    chambres_service=Depends(get_chambres_service),  # Service de gestion des chambres
    client=Depends(get_http_client),  # Client HTTP pour les requêtes externes
):
    """
    Point d'entrée pour récupérer les informations des chambres.
    Transmet la requête au service approprié avec les paramètres nécessaires.
    """
    return await chambres_service.get_chambres(
        path=path, request=request, client=client
    )
