# Import des modules nécessaires de FastAPI


from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated

from app.dependancies.auth import get_current_user, get_dynamic_permissions
from app.dependancies.httpx_client import get_http_client
from app.schemas.user import User
from app.services.chambres_liste import get_chambres_liste_service

# Création du routeur pour les chambres avec préfixe et tag
router = APIRouter(prefix="/chambres-liste", tags=["chambres_liste"])


@router.get("/{path:path}")
async def read_all_chambres(
    path: str,  # Chemin de la requête
    request: Request,  # Requête HTTP entrante
    current_user: Annotated[User, Depends(get_current_user)],
    internal_token: Annotated[str, Depends(get_dynamic_permissions("get", "chambres"))],
    chambres_liste_service=Depends(
        get_chambres_liste_service
    ),  # Service de gestion des chambres
    client=Depends(get_http_client),  # Client HTTP pour les requêtes externes
):
    """
    Point d'entrée pour récupérer les informations des chambres.
    Transmet la requête au service approprié avec les paramètres nécessaires.
    """
    return await chambres_liste_service.get_chambres(
        path=path, request=request, client=client, internal_token=internal_token
    )
