"""
Router pour les endpoints ML de prédiction de durée d'hospitalisation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.dependancies.httpx_client import get_http_client
from app.services.ml import get_ml_service
from app.schemas.user import User
from app.dependancies.auth import get_current_user, get_dynamic_permissions


router = APIRouter(
    prefix="/ml",
    tags=["ml"],
)


@router.get("/{path:path}")
async def get_ml(
    path: str,
    request: Request,
    internal_token: Annotated[str, Depends(get_dynamic_permissions("get", "ml"))],
    current_user: Annotated[User, Depends(get_current_user)],
    ml_service=Depends(get_ml_service),
    client=Depends(get_http_client),
):
    """Récupère l'historique des prédictions validées."""
    return await ml_service.get_ml(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )


@router.post("/{path:path}")
async def post_ml(
    path: str,
    request: Request,
    internal_token: Annotated[str, Depends(get_dynamic_permissions("post", "ml"))],
    current_user: Annotated[User, Depends(get_current_user)],
    ml_service=Depends(get_ml_service),
    client=Depends(get_http_client),
):
    """Effectue une prédiction ou valide une prédiction existante."""
    return await ml_service.post_ml(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )
