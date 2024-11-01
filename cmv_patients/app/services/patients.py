from fastapi import Request
from sqlalchemy.orm import Session

from app.repositories.patients_crud import PgPatientsRepository
from app.utils.logging_setup import LoggerSetup


# Retourne une instance de la classe PgPatientsRepository
def get_patients_repository():
    return PgPatientsRepository()


# Initialisation du service Patients
def get_patients_service():
    return PatientsService(get_patients_repository())


class PatientsService:
    logger = LoggerSetup()
    patients_repository: PgPatientsRepository

    def __init__(self, patients_repository: PgPatientsRepository):
        self.patients_repository = patients_repository

    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str,
        order: str,
        user_id: int,
        role: str,
        request: Request,
    ) -> dict:
        self.logger.write_log(
            f"{role} - {user_id} - {request.method} - read patients ", request
        )
        return await self.patients_repository.read_all_patients(
            db=db, page=page, limit=limit, field=field, order=order
        )

    async def search_patients(
        self,
        db: Session,
        search: str,
        page: int,
        limit: int,
        field: str,
        order: str,
        user_id: int,
        role: str,
        request: Request,
    ) -> dict:
        self.logger.write_log(
            f"{role} - {user_id} - {request.method} - search patients ", request
        )

        return await self.patients_repository.search_patients(
            db=db, search=search, page=page, limit=limit, field=field, order=order
        )
