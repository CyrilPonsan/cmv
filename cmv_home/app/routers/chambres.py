from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependancies.db_session import get_db
from ..dependancies.jwt import get_current_active_user
from ..schemas.schemas import Chambre
from ..schemas.user import User
from ..crud.chambre_crud import get_chambres, get_chambre_detail


router = APIRouter(prefix="/chambres", tags=["chambres"])


# retourne les détails d'une chambre
@router.get("/{chambre_id}")
async def read_chambre_detail(
    chambre_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db=Depends(get_db),
):
    try:
        return get_chambre_detail(db, chambre_id)
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Un problème est survenu.",
        )


# retourne la liste des chambres
@router.get("/", response_model=list[Chambre])
async def read_chambres(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db=Depends(get_db),
):
    try:
        return get_chambres(db)
    except HTTPException as e:
        print(e.detail)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Un problème est survenu",
        )
