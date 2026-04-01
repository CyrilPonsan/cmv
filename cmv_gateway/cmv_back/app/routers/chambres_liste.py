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
    path: str,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    chambres_token: Annotated[str, Depends(get_dynamic_permissions("get", "chambres"))],
    patients_token: Annotated[str, Depends(get_dynamic_permissions("get", "patients"))],
    chambres_liste_service=Depends(get_chambres_liste_service),
    client=Depends(get_http_client),
):
    return await chambres_liste_service.get_chambres(
        path=path,
        request=request,
        client=client,
        chambres_token=chambres_token,
        patients_token=patients_token,
    )
