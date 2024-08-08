from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends

from ..dependancies.db_session import get_db
from ..dependancies.jwt import get_current_active_user
from ..schemas.user import User
from ..schemas.schemas import Service
from ..crud.service_crud import get_services

router = APIRouter(prefix="/services", tags=["services"])


# retourne la liste des services et des chambres qui leur sont associées
@router.get("/", response_model=list[Service])
async def read_services(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db=Depends(get_db),
):
    try:
        return get_services(db)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Un problème est survenu",
        )
