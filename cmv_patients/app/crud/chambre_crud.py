from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..sql.models import Chambre, Service


def get_chambres(db: Session):
    return db.query(Chambre).all()


def get_chambre_detail(db: Session, chambre_id: int):
    chambre = db.query(Chambre).filter(Chambre.id == chambre_id).first()
    if not chambre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La chambre n'existe pas.",
        )
    return chambre


# Retourne la liste des chambres avec pagination
def get_rooms_with_pagination(db: Session, page: int, limit: int):
    # Vérifie que le numéro de page est valide
    if page < 1:
        page = 1

    # Vérifie que la limite d'éléments à afficher est valide
    if limit < 1:
        limit = 10

    # Requête principale
    query = db.query(Chambre, Service).join(Service, Chambre.service_id == Service.id)

    # Appliquer le tri
    query = query.order_by(Service.nom.asc(), Chambre.numero.asc())

    # Retourne le nombre total de chambres et calcule le nombre total de pages
    total_rooms = db.query(Chambre).count()
    total_pages = (total_rooms + limit - 1) // limit

    # Vérifie que le numéro de page envoyée par le frontend n'est pas supérieur au nombre total de page
    if page > total_pages:
        page = 1
        total_rooms = db.query(Chambre).count()
        total_pages = (total_rooms + limit - 1) // limit

    # Calcule l'offset pour la pagination et retourne le résultat final de la requête
    offset = (page - 1) * limit
    paginated_rooms = query.offset(offset).limit(limit).all()

    # Sérialisation du résultat de la requête
    rooms = [
        {
            "id": room.Chambre.id,
            "numero": room.Chambre.numero,
            "service": room.Service,
        }
        for room in paginated_rooms
    ]

    return {"rooms": rooms, "total_pages": total_pages}
