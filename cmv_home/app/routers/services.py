from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends

from ..dependancies.db_session import get_db
from ..schemas.schemas import PaginatedRooms, Service
from ..crud.service_crud import get_services
from ..crud.chambre_crud import get_rooms_with_pagination
from ..dependancies.auth import get_current_user

router = APIRouter(prefix="/services", tags=["services"])


# retourne la liste des services et des chambres qui leur sont associées
@router.get("/", response_model=list[Service])
async def read_services(
    is_auth: Annotated[bool, Depends(get_current_user)],
    db=Depends(get_db),
):
    try:
        print("toto services")
        return get_services(db)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Un problème est survenu",
        )


@router.get("/rooms", response_model=PaginatedRooms)
async def get_paginated_rooms(page: int = 1, limit: int = 10, db=Depends(get_db)):
    return get_rooms_with_pagination(db, page, limit)
