from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.patients import ReadAllPatients
from app.schemas.schemas import Patient
from app.schemas.user import InternalPayload
from app.services.patients import get_patients_service

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


@router.get("/", response_model=ReadAllPatients)
async def read_patients(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    page: int | None = 1,
    limit: int | None = 10,
    field: str | None = "nom",
    order: str | None = "asc",
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    return await patients_service.read_all_patients(
        db=db,
        page=page,
        limit=limit,
        field=field,
        order=order,
        request=request,
        user_id=payload["user_id"],
        role=payload["role"],
    )
