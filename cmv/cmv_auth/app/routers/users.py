from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.dependancies.db_session import get_db
from app.dependancies.jwt import get_current_active_user
from app.schemas.user import RegisterUser, User
from ..settings import models
from app.repositiries.user_crud import create_user
from ..services.redis.users import cache_data
from ..repositiries.user_crud import get_all_users

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/")
async def read_all_users(db=Depends(get_db)):
    @cache_data(expire_time=5 * 3600, key="all_users")
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
