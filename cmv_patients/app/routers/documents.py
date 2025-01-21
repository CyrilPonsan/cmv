# Import des modules nécessaires
import os
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.schemas import SuccessWithMessage
from app.schemas.user import InternalPayload
from app.services.documents import get_documents_service
from app.sql.models import DocumentType
from app.utils.logging_setup import LoggerSetup

# Création du router avec le préfixe /documents et le tag "documents" pour le regroupement dans la documentation
router = APIRouter(prefix="/documents", tags=["documents"])
# Initialisation du logger pour tracer les actions
logger = LoggerSetup()


# Fonction de validation du type de document
# Vérifie si le type fourni est bien un type valide défini dans l'enum DocumentType
def validate_document_data(document_type: DocumentType = Form(...)):
    # Vérifie si le type de document est valide en le comparant aux valeurs de l'enum
    if document_type not in DocumentType:
        raise HTTPException(status_code=400, detail="Invalid document type")
    return document_type


# Route pour créer un document à partir d'un fichier et de données présentes dans un form data
# Endpoint: POST /documents/create/{patient_id}
# Retourne un message de succès avec le statut de l'opération
@router.post("/create/{patient_id}", response_model=SuccessWithMessage)
async def create_document(
    request: Request,
    payload: Annotated[
        InternalPayload, Depends(check_authorization)
    ],  # Payload contenant les infos d'authentification de l'utilisateur
    patient_id: int,  # ID du patient pour lequel on crée le document
    data: DocumentType = Depends(
        validate_document_data
    ),  # Type de document validé via la fonction validate_document_data
    file: UploadFile = File(...),  # Fichier PDF à uploader
    documents_service=Depends(
        get_documents_service
    ),  # Service gérant les opérations sur les documents
    db=Depends(get_db),  # Session de base de données pour les opérations SQL
):
    # Série de vérifications sur le fichier uploadé pour s'assurer qu'il s'agit bien d'un PDF valide

    # 1. Vérification du content-type
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="not_pdf")

    # 2. Vérification de l'extension du fichier
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="not_pdf_extension")

    # Enregistrement de l'action dans les logs avec les informations de l'utilisateur
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - upload - {patient_id}",
        request,
    )

    # Lecture du contenu binaire du fichier uploadé
    contents = await file.read()

    # 3. Vérification de la signature PDF dans les premiers octets du fichier
    # Un fichier PDF valide commence toujours par la signature %PDF
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="not_valid_pdf")

    # Sauvegarde temporaire du fichier sur le serveur pour vérification supplémentaire si nécessaire
    temp_file_path = f"uploaded_{file.filename}"
    try:
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # Appel au service pour créer le document dans la base de données et le stocker sur S3
        await documents_service.create_document(
            db=db,
            file_contents=contents,
            type_document=data,
            patient_id=patient_id,
        )
    finally:
        # Suppression du fichier temporaire
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Retour d'une réponse de succès à l'utilisateur
    return {"success": True, "message": "document_created"}


# Route pour télécharger un document
# Endpoint: GET /documents/download/{document_id}
# Retourne le fichier PDF demandé
@router.get("/download/{document_id}")
async def download_document(
    request: Request,
    payload: Annotated[
        InternalPayload, Depends(check_authorization)
    ],  # Vérification des droits d'accès
    document_id: int,  # ID du document à télécharger
    documents_service=Depends(
        get_documents_service
    ),  # Service de gestion des documents
    db=Depends(get_db),  # Session de base de données
):
    # Enregistrement de l'action de téléchargement dans les logs
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - download - {document_id}",
        request,
    )
    # Récupération du fichier depuis le stockage S3
    file_content, filename = await documents_service.download_file_from_s3(
        db=db, document_id=document_id
    )

    # Retourne le fichier PDF avec les headers appropriés pour l'affichage dans le navigateur
    return Response(
        content=file_content.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# Route pour supprimer un document
# Endpoint: DELETE /documents/delete/{document_id}
# Retourne un message de succès après la suppression
@router.delete("/delete/{document_id}", response_model=SuccessWithMessage)
async def delete_document(
    request: Request,
    payload: Annotated[
        InternalPayload, Depends(check_authorization)
    ],  # Vérification des droits d'accès
    document_id: int,  # ID du document à supprimer
    documents_service=Depends(
        get_documents_service
    ),  # Service de gestion des documents
    db=Depends(get_db),  # Session de base de données
):
    # Enregistrement de l'action de suppression dans les logs
    logger.write_log(
        f"{payload['role']} - {payload['user_id']} - {request.method} - delete - {document_id}",
        request,
    )
    # Suppression du document via le service et retour du résultat
    return await documents_service.delete_document_by_id(db=db, document_id=document_id)
