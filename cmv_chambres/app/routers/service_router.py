from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.services.services import get_service_service

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/")
async def read_all_services(db: Session = Depends(get_db)):
    return await get_service_service().read_all_services(db)
