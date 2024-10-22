from fastapi import Request
from sqlalchemy.orm import Session
from ..sql.models import Patient
from ..utils.logging_setup import LoggerSetup

logger = LoggerSetup()


class Patients:
    def __init__(self):
        pass

    @staticmethod
    async def read_patients(db: Session, user_id: int, role: str, request: Request):
        logger.write_log(f"{role} - {user_id} - {request.method} - read patients ", request)
        return db.query(Patient).all()
