# Import des types et annotations nécessaires
from typing import Annotated

# Import des dépendances FastAPI
from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.orm import Session

from app.dependancies.auth import get_permissions
from app.dependancies.db_session import get_db
from app.schemas.patients import CreateAdmission
from app.schemas.user import InternalPayload

# Import des services et dépendances personnalisés
from app.services.admissions import AdmissionService
from app.services.patients import PatientsService, get_patients_service

# Création du routeur FastAPI
router = APIRouter()


@router.post("/admissions")
async def create_admission(
    request: Request,
    data: Annotated[CreateAdmission, Body()],  # Données de l'admission à créer
    internal_payload: Annotated[InternalPayload, Depends(get_permissions)],
    patients_service: PatientsService = Depends(get_patients_service),
    db: Session = Depends(get_db),  # Injection de la session de base de données
):
    """
    Crée une nouvelle admission pour un patient.

    Args:
        data (CreateAdmission): Les données de l'admission à créer
        db (Session): La session de base de données

    Returns:
        dict: Les détails de l'admission créée
    """
    return await AdmissionService(db).create_admission(
        data,
        internal_payload,
        request,
    )
