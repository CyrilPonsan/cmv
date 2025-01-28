# Import des modules nécessaires pour le typage et FastAPI
from typing import Annotated

from fastapi import APIRouter, Depends

# Import des dépendances pour l'authentification et le modèle utilisateur
from app.dependancies.auth import get_current_user
from app.schemas.user import User


# Configuration du routeur pour les utilisateurs avec préfixe et tag
router = APIRouter(
    prefix="/users",  # Préfixe pour toutes les routes utilisateurs
    tags=["users"],  # Tag pour le regroupement dans la documentation
)


# Point d'entrée pour obtenir le rôle de l'utilisateur connecté
@router.get("/me", response_model=dict)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retourne le rôle de l'utilisateur actuellement authentifié

    Args:
        current_user: L'utilisateur actuellement connecté (injecté via la dépendance)

    Returns:
        dict: Un dictionnaire contenant le nom du rôle de l'utilisateur
    """
    return {"role": current_user.role.name}


"""
# Routes commentées pour référence future

# Point d'entrée pour obtenir la liste de tous les utilisateurs (mise en cache)
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


# Point d'entrée pour l'enregistrement d'un nouvel utilisateur
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
