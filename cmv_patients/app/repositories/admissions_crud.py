from app.sql.models import Admission
from sqlalchemy.orm import Session


class PgAdmissionsRepository:
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
