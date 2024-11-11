from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.user import InternalPayload
from app.services.documents import get_documents_service
from app.sql.models import DocumentType
from app.utils.logging_setup import LoggerSetup

router = APIRouter(prefix="/documents", tags=["documents"])
logger = LoggerSetup()


def validate_document_data(document_type: DocumentType = Form(...)):
    if document_type not in DocumentType:
        raise HTTPException(status_code=400, detail="Invalid document type")
    return document_type


# Route pour créer un document à partir d'un fichier et de données présentes dans un form data
@router.post("/create/{patient_id}")
async def create_document(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patient_id: int,
    data: DocumentType = Depends(validate_document_data),
    file: UploadFile = File(...),
    documents_service=Depends(get_documents_service),
    db=Depends(get_db),
):
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - search patients",
        request,
    )
    print(f"FILENAME: {file.filename}")
    print(f"DOCUMENT TYPE: {data}")

    contents = await file.read()
    with open(f"uploaded_{file.filename}", "wb") as f:
        f.write(contents)

    return await documents_service.create_document(
        db=db,
        file_contents=contents,
        type_document=data,
        patient_id=patient_id,
    )
