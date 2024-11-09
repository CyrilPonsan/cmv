from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.user import InternalPayload
from app.services.documents import get_documents_service
from app.utils.logging_setup import LoggerSetup

router = APIRouter(prefix="/documents", tags=["documents"])
logger = LoggerSetup()


@router.get("/{patient_id}")
async def read_all_patient_documents(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patient_id: int,
    documents_service=Depends(get_documents_service),
    db=Depends(get_db),
):
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - read documents : {patient_id}",
        request,
    )
    return await documents_service.read_all_patient_documents(
        db=db, patient_id=patient_id, request=request, payload=payload
    )
