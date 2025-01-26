from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.admissions import AdmissionService
from app.dependancies.db_session import get_db
from app.schemas.schemas import CreateAdmission


router = APIRouter()


@router.post("/admissions")
async def create_admission(data: CreateAdmission, db: Session = Depends(get_db)):
    return await AdmissionService(db).create_admission(data)
