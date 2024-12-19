from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy.orm import Session

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.patients import (
    CreatePatient,
    PatientsParams,
    PostPatientResponse,
    ReadAllPatients,
    SearchPatientsParams,
    DetailPatient,
)
from app.schemas.user import InternalPayload
from app.services.patients import get_patients_service
from app.utils.logging_setup import LoggerSetup

# Création du router FastAPI pour les endpoints patients
router = APIRouter(prefix="/patients", tags=["patients"])
# Initialisation du logger
logger = LoggerSetup()


# Endpoint pour créer un nouveau patient
@router.post("/", response_model=PostPatientResponse, status_code=201)
async def create_patient(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    data: Annotated[CreatePatient, Body()],
    db: Session = Depends(get_db),
    patients_service=Depends(get_patients_service),
):
    """
    Crée un nouveau patient dans la base de données.

    Args:
        data (Patient): Les données du patient à créer
        db (Session): La session de base de données

    Returns:
        Patient: Les données du patient créé

    Raises:
        HTTPException: En cas d'erreur lors de la création
    """
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - create patient",
        request,
    )
    new_patient = await patients_service.create_patient(db=db, data=data)
    return {
        "success": True,
        "message": "Patient créé avec succès",
        "id_patient": new_patient.id_patient,
    }


# Endpoint pour récupérer la liste des patients avec pagination et tri
@router.get("/", response_model=ReadAllPatients)
async def read_patients(
    request: Request,
    params: Annotated[PatientsParams, Query()],
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    """
    Récupère une liste paginée et triée de tous les patients.

    Args:
        request (Request): La requête HTTP
        params (PatientsParams): Les paramètres de pagination et tri
        payload (InternalPayload): Les informations d'authentification
        patients_service: Le service de gestion des patients
        db: La session de base de données

    Returns:
        ReadAllPatients: La liste des patients avec métadonnées de pagination
    """
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - read patients",
        request,
    )
    return await patients_service.read_all_patients(
        db=db,
        page=params.page,
        limit=params.limit,
        field=params.field,
        order=params.order,
    )


# Endpoint pour rechercher des patients avec filtres, pagination et tri
@router.get("/search", response_model=ReadAllPatients)
async def search_patients(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    params: Annotated[SearchPatientsParams, Query()],
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    """
    Recherche des patients selon des critères avec pagination et tri.

    Args:
        request (Request): La requête HTTP
        payload (InternalPayload): Les informations d'authentification
        params (SearchPatientsParams): Les paramètres de recherche, pagination et tri
        patients_service: Le service de gestion des patients
        db: La session de base de données

    Returns:
        ReadAllPatients: La liste filtrée des patients avec métadonnées de pagination
    """
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - search patients",
        request,
    )
    return await patients_service.search_patients(
        db=db,
        search=params.search,
        page=params.page,
        limit=params.limit,
        field=params.field,
        order=params.order,
    )


# Endpoint pour récupérer les détails d'un patient spécifique
@router.get("/detail/{patient_id}", response_model=DetailPatient)
async def read_patient(
    request: Request,
    patient_id: int,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patients_service=Depends(get_patients_service),
    db: Session = Depends(get_db),
):
    """
    Récupère les informations détaillées d'un patient par son ID.

    Args:
        request (Request): La requête HTTP
        patient_id (int): L'identifiant du patient
        payload (InternalPayload): Les informations d'authentification
        patients_service: Le service de gestion des patients
        db (Session): La session de base de données

    Returns:
        DetailPatient: Les informations détaillées du patient
    """
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - read patient {patient_id}",
        request,
    )
    return await patients_service.detail_patient(
        db=db,
        patient_id=patient_id,
    )


# Endpoint pour mettre à jour les données d'un patient
@router.put("/{patient_id}", response_model=DetailPatient)
async def update_patient(
    request: Request,
    patient_id: int,
    data: Annotated[CreatePatient, Body()],
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patients_service=Depends(get_patients_service),
    db: Session = Depends(get_db),
):
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - update patient {patient_id}",
        request,
    )
    return await patients_service.update_patient(
        db=db,
        patient_id=patient_id,
        data=data,
    )
