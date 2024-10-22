from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..dependancies.auth import check_authorization
from ..dependancies.db_session import get_db
from ..schemas.schemas import Patient
from ..controller.patients import Patients
from ..schemas.user import InternalPayload

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
async def read_patients(request: Request, payload: Annotated[InternalPayload, Depends(check_authorization)],
                        db=Depends(get_db)):
    return await Patients.read_patients(db, payload["user_id"], payload["role"], request)
