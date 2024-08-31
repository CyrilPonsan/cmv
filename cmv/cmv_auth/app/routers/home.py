import httpx
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status

from ..utils.config import HOME_SERVICE
from ..schemas.user import User
from ..dependancies.jwt import get_current_active_user

router = APIRouter(
    prefix="/home",
    tags=["home"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# requêtes utilisant la méthode 'GET' à destination de l'API Home
@router.get("/{path:path}")
async def read_chambres(
    path: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        # construction de l'url
        url = f"{HOME_SERVICE}/{path}/"
        headers = {"Authorization": f"Bearer {token}"}
        # envoi de la requête
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                follow_redirects=True,
            )
            # gestion d'une réponse positive
            if response.status_code == 200:
                return response.json()
            else:
                # gestion des erreurs retournées par le service accueil
                result = response.json()
                raise HTTPException(
                    status_code=response.status_code, detail=result["detail"]
                )
    except HTTPException as e:
        print(e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    # gestion des erreurs globales (réseau, bdd)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Un problème est survenu.",
        )
