# Import des modules nécessaires
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.user import InternalPayload
from app.services.documents import get_documents_service
from app.sql.models import DocumentType
from app.utils.logging_setup import LoggerSetup

# Création du router avec le préfixe /documents
router = APIRouter(prefix="/documents", tags=["documents"])
logger = LoggerSetup()


# Fonction de validation du type de document
def validate_document_data(document_type: DocumentType = Form(...)):
    # Vérifie si le type de document est valide
    if document_type not in DocumentType:
        raise HTTPException(status_code=400, detail="Invalid document type")
    return document_type


# Route pour créer un document à partir d'un fichier et de données présentes dans un form data
@router.post("/create/{patient_id}")
async def create_document(
    request: Request,
    payload: Annotated[
        InternalPayload, Depends(check_authorization)
    ],  # Payload contenant les infos d'authentification
    patient_id: int,  # ID du patient concerné
    data: DocumentType = Depends(validate_document_data),  # Type de document validé
    file: UploadFile = File(...),  # Fichier uploadé
    documents_service=Depends(
        get_documents_service
    ),  # Service de gestion des documents
    db=Depends(get_db),  # Session de base de données
):
    # Vérifier que le fichier est un PDF via le content-type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400, detail="Le fichier doit être au format PDF"
        )

    # Vérifier l'extension du fichier
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="L'extension du fichier doit être .pdf"
        )

    # Journalisation de l'action
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - upload - {patient_id}",
        request,
    )

    # Lecture du contenu du fichier
    contents = await file.read()

    # Vérification de la signature PDF dans les premiers octets du fichier
    if not contents.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400, detail="Le contenu du fichier n'est pas un PDF valide"
        )

    # Sauvegarde temporaire du fichier sur le serveur
    with open(f"uploaded_{file.filename}", "wb") as f:
        f.write(contents)

    # Création du document dans la base de données via le service
    await documents_service.create_document(
        db=db,
        file_contents=contents,
        type_document=data,
        patient_id=patient_id,
    )

    # Retour d'une réponse de succès
    return {"success": True, "message": "Le document a été téléversé avec succès."}


# Route pour télécharger un document
@router.get("/download/{document_id}")
async def download_document(
    request: Request,
    payload: Annotated[InternalPayload, Depends(check_authorization)],
    document_id: int,
    documents_service=Depends(get_documents_service),
    db=Depends(get_db),
):
    # Journalisation de l'action
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - download - {document_id}",
        request,
    )
    # Télécharge le fichier depuis S3
    file_content, filename = await documents_service.download_file_from_s3(
        db=db, document_id=document_id
    )

    return StreamingResponse(
        file_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
