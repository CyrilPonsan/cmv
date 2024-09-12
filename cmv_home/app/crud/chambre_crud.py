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


# retourne la liste des chambres avec pagination
def get_rooms_with_pagination(db: Session, page: int, limit: int):
    if page < 1:
        page = 1


    # Requête principale
    query = db.query(Chambre, Service.nom.label("service_nom")).join(
        Service, Chambre.service_id == Service.id
    )

    # Appliquer le tri
    query = query.order_by(Service.nom.asc(), Chambre.numero.asc())

    total_rooms = db.query(Chambre).count()
    total_pages = (total_rooms + limit - 1) // limit

    if page > total_pages:
        page = 1
        total_rooms = db.query(Chambre).count()
        total_pages = (total_rooms + limit - 1) // limit


    offset = (page - 1) * limit
    paginated_rooms = query.offset(offset).limit(limit).all()

    for room in paginated_rooms:
        print(f"chambre : {room.Chambre.numero} - {room.service_nom}")

    rooms = [
        {
            "id": room.Chambre.id,
            "numero": room.Chambre.numero,
            "service": room.service_nom,
        }
        for room in paginated_rooms
    ]

    return {"rooms": rooms, "total_pages": total_pages}
