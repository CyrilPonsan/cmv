from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from ..dependancies.db_session import get_db
from ..schemas.schemas import Patient
from ..controller.patients import Patients


router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/")
def create_patient(data: Annotated[Patient, Body()], db: Session = Depends(get_db)):
    try:
        return data
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="oops",
        )


@router.get("/")
async def read_patients(db=Depends(get_db)):
    print("coucou les patients")
    return await Patients.read_patients(db)
