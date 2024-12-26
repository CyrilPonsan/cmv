from typing import Annotated

from fastapi import APIRouter, Depends, Request, File, Form, UploadFile

from app.dependancies.httpx_client import get_http_client
from app.services.patients import get_patients_service
from app.schemas.user import User
from app.dependancies.auth import get_current_user, get_dynamic_permissions

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


@router.get("/download/{path:path}")
async def download_document(
    request: Request,
    path: str,
    internal_token: Annotated[
        str, Depends(get_dynamic_permissions("get", "documents"))
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    return await patients_service.get_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )


# Requêtes utilisant la méthode 'GET' à destination de l'API Patients
@router.get("/{path:path}")
async def read_patients(
    path: str,
    request: Request,
    internal_token: Annotated[str, Depends(get_dynamic_permissions("get", "patients"))],
    current_user: Annotated[User, Depends(get_current_user)],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    return await patients_service.get_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )


# Requêtes utilisant la méthode 'POST' à destination de l'API Patients pour le téléversement de documents
@router.post("/upload/{path:path}")
async def create_document(
    request: Request,
    path: str,
    internal_token: Annotated[
        str, Depends(get_dynamic_permissions("post", "documents"))
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    patients_service=Depends(get_patients_service),
    file: Annotated[UploadFile, File()] = None,
    document_type: str = Form(...),
):
    return await patients_service.forward_document(
        current_user=current_user,
        path=path,
        file=file,
        internal_token=internal_token,
        document_type=document_type,
        request=request,
    )


# Requêtes utilisant la méthode 'POST' à destination de l'API Patients
@router.post("/{path:path}")
async def post_patients(
    current_user: Annotated[User, Depends(get_current_user)],
    path: str,
    request: Request,
    internal_token: Annotated[
        str, Depends(get_dynamic_permissions("post", "patients"))
    ],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    data = await request.json()
    print(f"NOM : {data['nom']}")
    return await patients_service.post_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )


# Requêtes utilisant la méthode 'DELETE' pour la suppression de documents
@router.delete("/delete/{path:path}")
async def delete_patients(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    path: str,
    internal_token: Annotated[
        str, Depends(get_dynamic_permissions("delete", "documents"))
    ],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    return await patients_service.delete_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )


# Requêtes utilisant la méthode 'PUT' pour la modification des données d'un patient
@router.put("/{path:path}")
async def put_patients(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    path: str,
    internal_token: Annotated[str, Depends(get_dynamic_permissions("put", "patients"))],
    patients_service=Depends(get_patients_service),
    client=Depends(get_http_client),
):
    return await patients_service.put_patients(
        current_user=current_user,
        path=path,
        internal_token=internal_token,
        client=client,
        request=request,
    )
