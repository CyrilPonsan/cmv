from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.services.admissions import AdmissionService
from app.dependancies.db_session import get_db
from app.schemas.patients import CreateAdmission


router = APIRouter()


@router.post("/admissions")
async def create_admission(
    data: Annotated[CreateAdmission, Body()],
    db: Session = Depends(get_db),
):
    return await AdmissionService(db).create_admission(data)
