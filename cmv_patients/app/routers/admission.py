# Import des types et annotations nécessaires
from typing import Annotated

# Import des dépendances FastAPI
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

# Import des services et dépendances personnalisés
from app.services.admissions import AdmissionService
from app.dependancies.db_session import get_db
from app.schemas.patients import CreateAdmission


# Création du routeur FastAPI
router = APIRouter()


@router.post("/admissions")
async def create_admission(
    data: Annotated[CreateAdmission, Body()],  # Données de l'admission à créer
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
    return await AdmissionService(db).create_admission(data)
