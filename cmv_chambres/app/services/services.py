from sqlalchemy.orm import Session

from app.repositories.service_crud import PgServiceRepository, ServiceRepository
from app.schemas.services import ServicesListItem


def get_service_repository():
    return PgServiceRepository()


# Initialisation du service Service
def get_service_service():
    return ServiceService(get_service_repository())


class ServiceService:
    service_repository: ServiceRepository

    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    async def read_all_services(self, db: Session) -> list[ServicesListItem]:
        return await self.service_repository.read_all_services(db)
