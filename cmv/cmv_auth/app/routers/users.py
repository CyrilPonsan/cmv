from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.dependancies.db_session import get_db
from app.dependancies.jwt import get_current_active_user
from app.schemas.user import RegisterUser, User
from app.sql.crud import create_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"role": current_user.role.name}


@router.post("/user/register")
def register_user(data: RegisterUser, db: Session = Depends(get_db)):
    result = create_user(db, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte enregistré avec cette adresse existe déjà",
        )
    return {"message": "Compte créé avec succès"}
