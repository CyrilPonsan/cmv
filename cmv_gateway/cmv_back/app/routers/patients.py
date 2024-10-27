from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.dependancies.httpx_client import get_http_client
from app.services.patients import get_patients_service
from app.schemas.user import User
from app.dependancies.auth import get_current_user, get_dynamic_permissions

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


# Requêtes utilisant la méthode 'GET' à destination de l'API Patients
@router.get("/{path:path}")
async def read_patients(
    path: str,
    request: Request,
    internal_token: Annotated[str, Depends(get_dynamic_permissions("get", "patients"))],
    current_user: Annotated[User, Depends(get_current_user)],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    print(f"TOTO PATH : {path}")
    return await patients_service.get_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )
