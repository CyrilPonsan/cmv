from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from ..dependancies.db_session import get_db
from ..schemas.schemas import PatientBase


router = APIRouter(prefix="/patient", tags=["patient"])


@router.post("/")
def create_patient(data: Annotated[PatientBase, Body()], db: Session = Depends(get_db)):
    try:
        return data
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="oops",
        )
