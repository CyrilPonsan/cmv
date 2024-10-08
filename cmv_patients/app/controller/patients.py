from sqlalchemy.orm import Session
from ..sql.models import Patient


class Patients:
    def __init__(self):
        pass

    @staticmethod
    async def read_patients(db: Session):
        return db.query(Patient).all()
