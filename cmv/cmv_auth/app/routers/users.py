from typing_extensions import Annotated
from app.dependancies.auth import get_dynamic_permissions
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.dependancies.db_session import get_db
from app.repositories.user_crud import create_user, get_all_users
from app.schemas.user import RegisterUser
from ..services.redis_cached_data import cache_data

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# retourne la liste de tous les utilisateurs depuis le cache si elle y est présente, sinon met la liste de tous les uitlisateurs dans le cache redis
@router.get("/")
async def read_all_users(
    _: Annotated[
        bool, Depends(get_dynamic_permissions(action="get", resource="services"))
    ],
    db=Depends(get_db),
):
    @cache_data(expire_time=5 * 60, key="all_users")
    def cached_users():
        return get_all_users(db)

    return await cached_users()


@router.post("/user/register")
def register_user(data: RegisterUser, db: Session = Depends(get_db)):
    result = create_user(db, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte enregistré avec cette adresse existe déjà",
        )
    return {"message": "Compte créé avec succès"}
