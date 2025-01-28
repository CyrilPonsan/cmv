import os
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.schemas import SuccessWithMessage
from app.schemas.user import InternalPayload
from app.sql.models import DocumentType
from app.utils.logging_setup import LoggerSetup
from app.services.patients import get_patients_service

# Création du router FastAPI pour les endpoints liés aux documents
router = APIRouter(prefix="/documents", tags=["documents"])
logger = LoggerSetup()


# Fonction de validation du type de document
def validate_document_data(document_type: DocumentType = Form(...)):
    if document_type not in DocumentType:
        raise HTTPException(status_code=400, detail="Invalid document type")
    return document_type


# Endpoint pour créer un nouveau document pour un patient
@router.post("/create/{patient_id}", response_model=SuccessWithMessage)
async def create_document(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    patient_id: int,
    data: DocumentType = Depends(validate_document_data),
    file: UploadFile = File(...),
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    # Vérifie que le fichier est bien un PDF (par le content-type)
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="not_pdf")

    # Vérifie que l'extension du fichier est .pdf
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="not_pdf_extension")

    # Enregistre l'action dans les logs
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - upload - {patient_id}",
        request,
    )

    # Lit le contenu du fichier
    contents = await file.read()

    # Vérifie que le contenu commence bien par la signature PDF
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="not_valid_pdf")

    # Crée un fichier temporaire pour stocker le PDF
    temp_file_path = f"uploaded_{file.filename}"
    try:
        # Écrit le contenu dans le fichier temporaire
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # Crée le document dans la base de données et le stocke sur S3
        await patients_service.create_patient_document(
            db=db,
            file_contents=contents,
            type_document=data,
            patient_id=patient_id,
        )
    finally:
        # Supprime le fichier temporaire
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return {"success": True, "message": "document_created"}


# Endpoint pour télécharger un document
@router.get("/download/{document_id}")
async def download_document(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    document_id: int,
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    # Enregistre l'action dans les logs
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - download - {document_id}",
        request,
    )
    # Récupère le contenu du fichier depuis S3
    file_content, filename = await patients_service.download_file_from_s3(
        db=db, document_id=document_id
    )

    # Retourne le fichier PDF avec les headers appropriés
    return Response(
        content=file_content.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# Endpoint pour supprimer un document
@router.delete("/delete/{document_id}", response_model=SuccessWithMessage)
async def delete_document(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    document_id: int,
    patients_service=Depends(get_patients_service),
    db=Depends(get_db),
):
    # Enregistre l'action dans les logs
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - delete - {document_id}",
        request,
    )
    return await patients_service.delete_document_by_id(db=db, document_id=document_id)
