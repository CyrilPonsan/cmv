from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependancies.auth import get_current_user
from app.schemas.user import User


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# Retourne le rôle d'un utilisateur authentifié
@router.get("/me", response_model=dict)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"role": current_user.role.name}


"""
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
"""
