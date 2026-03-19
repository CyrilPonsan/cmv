# Import des types et annotations nécessaires
from typing import Annotated

# Import des dépendances FastAPI
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.schemas.patients import CloseAdmission, CreateAdmission

# Import des services et dépendances personnalisés
from app.services.admissions import AdmissionService, get_admissions_service

# Création du routeur FastAPI
router = APIRouter(prefix="/admissions", tags=["admissions"])


@router.post("/")
async def create_admission(
    data: Annotated[CreateAdmission, Body()],  # Données de l'admission à créer
    admissions_service: AdmissionService = Depends(get_admissions_service),
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
    return await admissions_service.create_admission(db, data)


@router.get("/{id_admission}")
async def get_admission(
    id_admission: int,
    admissions_service: AdmissionService = Depends(get_admissions_service),
    db: Session = Depends(get_db),
):
    return await admissions_service.get_admission(db, id_admission)


@router.put("/{id_admission}/close")
async def close_admission(
    id_admission: int,
    data: Annotated[CloseAdmission, Body()],
    admissions_service: AdmissionService = Depends(get_admissions_service),
    db: Session = Depends(get_db),
):
    return await admissions_service.close_admission(db, id_admission, data)
