# Import des modules nécessaires
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Import des dépendances et services
from app.dependancies.db_session import get_db
from app.services.services import get_service_service
from app.schemas.services import ServicesList, ServicesListItem

# Création du routeur pour les endpoints liés aux services
router = APIRouter(prefix="/services", tags=["services"])


@router.get("/simple", response_model=list[ServicesList])
async def read_simple_services(db: Session = Depends(get_db)):
    """
    Récupère une liste simplifiée des services disponibles.
    Cette route retourne uniquement les informations de base des services,
    sans les détails des chambres et des réservations.

    Args:
        db (Session): Session de base de données injectée par FastAPI

    Returns:
        list[ServicesListItem]: Liste simplifiée des services
    """
    return await get_service_service().get_simple_services_list(db)


@router.get("/", response_model=list[ServicesListItem])
async def read_all_services(db: Session = Depends(get_db)):
    """
    Récupère la liste de tous les services disponibles.

    Args:
        db (Session): Session de base de données injectée par FastAPI

    Returns:
        list[ServicesListItem]: Liste des services avec leurs informations
    """
    return await get_service_service().read_all_services(db)
