# Import des types et annotations nécessaires
from typing import Annotated
from venv import logger

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependancies.auth import get_permissions
from app.dependancies.db_session import get_db
from app.schemas.patients import Admission, CreateAdmission
from app.schemas.user import InternalPayload

# Import des services et dépendances personnalisés
from app.services.admissions import get_admissions_service
from app.services.patients import get_patients_service

# Import des dépendances FastAPI

# Création du routeur FastAPI
router = APIRouter()


@router.get("/admissions/{admission_id}", response_model=Admission)
async def get_admission_detail(
    admission_id: int,
    request: Request,
    internal_payload: Annotated[InternalPayload, Depends(get_permissions)],
    admission_service=Depends(get_admissions_service),
    db: Session = Depends(get_db),
) -> Admission:
    return await admission_service.get_admission(db=db, admission_id=admission_id)


@router.post("/admissions")
async def create_admission(
    request: Request,
    data: Annotated[CreateAdmission, Body()],  # Données de l'admission à créer
    internal_payload: Annotated[InternalPayload, Depends(get_permissions)],
    admission_service=Depends(get_admissions_service),
    patient_service=Depends(get_patients_service),
    db: Session = Depends(get_db),
):
    """
    Crée une nouvelle admission pour un patient.

    Args:
        data (CreateAdmission): Les données de l'admission à créer
        db (Session): La session de base de données

    Returns:
        dict: Les détails de l'admission créée
    """
    existing_patient = await patient_service.detail_patient(
        db, data.patient_id, payload=internal_payload
    )
    if not existing_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
        )
    # Check admissions: detail_patient returns a dict or ORM object
    if isinstance(existing_patient, dict):
        admission = existing_patient.get("latest_admission")
        has_active_admission = admission and not admission.get("sorti_le")
    else:
        has_active_admission = (
            existing_patient.admissions
            and existing_patient.admissions[0].sorti_le is None
        )
    if has_active_admission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="patient_already_admitted"
        )
    if data.ambulatoire is False and data.service_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="service_id_missing"
        )
    return await admission_service.create_admission(
        db=db, data=data, internal_payload=internal_payload, request=request
    )


@router.put("/admissions/closure", response_model=Admission)
async def update_admission(
    request: Request,
    data: Annotated[Admission, Body()],
    internal_payload: Annotated[InternalPayload, Depends(get_permissions)],
    admission_service=Depends(get_admissions_service),
    db: Session = Depends(get_db),
) -> Admission:
    return await admission_service.update_admission(
        db=db,
        data=data,
        internal_payload=internal_payload,
        request=request,
    )
