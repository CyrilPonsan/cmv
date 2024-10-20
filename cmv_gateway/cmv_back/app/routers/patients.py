from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.services.patients import get_patients_service
from ..schemas.user import User
from ..dependancies.auth import get_dynamic_permissions

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


# Requêtes utilisant la méthode 'GET' à destination de l'API Patients
@router.get("/{path:path}")
async def read_patients(
    path: str,
    request: Request,
    current_user: Annotated[User, Depends(get_dynamic_permissions("get", "patients"))],
    patients_service=Depends(get_patients_service),
):
    return await patients_service.get_patients(path=path, cookie=request.cookies)
