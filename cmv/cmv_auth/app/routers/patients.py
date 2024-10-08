import httpx
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from ..utils.config import PATIENTS_SERVICE
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
    # Construction de l'url
    url = f"{PATIENTS_SERVICE}/{path}/"
    print(f"URL : {current_user}")

    # Récupération des cookies de la session
    cookies = request.cookies

    return Patients().read_patients(url, cookies)


class Patients:
    def __init__(self):
        pass

    async def read_patients(self, url: str, cookies: dict):
        async with httpx.AsyncClient(cookies=cookies) as client:
            response = await client.get(
                url,
                follow_redirects=True,
            )
            if response.status_code == 200:
                return response.json()
            else:
                result = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=result.get("detail", "Une erreur s'est produite."),
                )
