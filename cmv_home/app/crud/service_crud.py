from sqlalchemy.orm import Session

from ..sql.models import Service


# retourne tous les services de la clinique
def get_services(db: Session):
    return db.query(Service).order_by(Service.nom).all()
