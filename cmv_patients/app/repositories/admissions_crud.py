from abc import ABC, abstractmethod

from app.sql.models import Admission
from sqlalchemy.orm import Session


class AdmissionsCrud(ABC):
    @abstractmethod
    async def create_admission(self, db: Session, admission: Admission) -> Admission:
        pass

    @abstractmethod
    async def delete_admission(self, db: Session, admission_id: int):
        pass

    @abstractmethod
    async def get_admission_by_id(self, db: Session, admission_id: int) -> Admission:
        pass


class PgAdmissionsRepository(AdmissionsCrud):
    async def create_admission(self, db: Session, admission: Admission) -> Admission:
        db.add(admission)
        db.commit()
        db.refresh(admission)

        return admission

    async def delete_admission(self, db: Session, admission_id: int):
        db.query(Admission).filter(Admission.id_admission == admission_id).delete()
        db.commit()

    async def get_admission_by_id(self, db: Session, admission_id: int) -> Admission:
        return (
            db.query(Admission).filter(Admission.id_admission == admission_id).first()
        )
