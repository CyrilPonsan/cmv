from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.patients import (
    PatientsParams,
    ReadAllPatients,
    SearchPatientsParams,
    DetailPatient,
)
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


# Retourne une liste de patients en fonction des paramètres de pagination et de tri
@router.get("/", response_model=ReadAllPatients)
async def read_patients(
    request: Request,
    params: Annotated[PatientsParams, Query()],
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    return await patients_service.read_all_patients(
        db=db,
        page=params.page,
        limit=params.limit,
        field=params.field,
        order=params.order,
        request=request,
        user_id=payload["user_id"],
        role=payload["role"],
    )


# Retourne une liste de patients en fonction des paramètres de recherche, de pagination et de tri
@router.get("/search", response_model=ReadAllPatients)
async def search_patients(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    params: Annotated[SearchPatientsParams, Query()],
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    return await patients_service.search_patients(
        db=db,
        search=params.search,
        page=params.page,
        limit=params.limit,
        field=params.field,
        order=params.order,
        request=request,
        user_id=payload["user_id"],
        role=payload["role"],
    )


# Retourne les informations d'un patient en fonction de son id
@router.get("/{patient_id}", response_model=DetailPatient)
async def read_patient(
    request: Request,
    patient_id: int,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patients_service=Depends(get_patients_service),
    db: Session = Depends(get_db),
):
    return await patients_service.detail_patient(
        db=db,
        patient_id=patient_id,
        user_id=payload["user_id"],
        role=payload["role"],
        request=request,
    )
