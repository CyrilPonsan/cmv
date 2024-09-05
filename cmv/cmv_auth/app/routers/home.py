import httpx
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from ..settings.config import HOME_SERVICE
from ..schemas.user import User
from ..dependancies.auth import get_current_user

router = APIRouter(
    prefix="/home",
    tags=["home"],
)


# requêtes utilisant la méthode 'GET' à destination de l'API Home
@router.get("/{path:path}")
async def read_chambres(
    path: str,
    current_user: Annotated[User, Depends(get_current_user)],  # Session-based user auth
    request: Request,  # Ajout de l'objet Request pour accéder aux cookies
):
    # construction de l'url
    url = f"{HOME_SERVICE}/{path}/"
    print(f"URL : {current_user}")

    # Récupération des cookies de la session
    cookies = request.cookies

    # envoi de la requête avec les cookies
    async with httpx.AsyncClient(cookies=cookies) as client:
        response = await client.get(
            url,
            follow_redirects=True,
        )
        # gestion d'une réponse positive
        if response.status_code == 200:
            return response.json()
        else:
            # gestion des erreurs retournées par le service accueil
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result.get("detail", "Une erreur s'est produite."),
            )
