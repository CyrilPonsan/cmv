import pytest
from io import BytesIO

from app.sql.models import DocumentType


@pytest.mark.asyncio
async def test_create_document_no_auth(ac):
    """Test creating a document without authentication"""
    response = await ac.post("/api/documents/create/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_create_document_wrong_token(ac, wrong_internal_token):
    """Test creating a document with invalid token"""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.post("/api/documents/create/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_create_document_patient_not_found(ac, internal_token):
    """Test creating a document for non-existent patient"""
    headers = {"Authorization": f"Bearer {internal_token}"}
    file_content = b"test content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    form_data = {"document_type": DocumentType.MISCELLANEOUS.value}

    response = await ac.post(
        "/api/documents/create/999", headers=headers, files=files, data=form_data
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "patient_not_found"}


@pytest.mark.asyncio
async def test_create_document_invalid_type(ac, internal_token, patients):
    """Test creating a document with invalid document type"""
    headers = {"Authorization": f"Bearer {internal_token}"}
    file_content = b"test content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    form_data = {"document_type": "INVALID_TYPE"}

    response = await ac.post(
        "/api/documents/create/1", headers=headers, files=files, data=form_data
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_document_success(ac, internal_token, patients, mocker):
    """Test successful document creation"""
    # Mock S3 upload
    mocker.patch(
        "app.services.documents.DocumentsService._upload_file_to_s3", return_value=True
    )

    headers = {"Authorization": f"Bearer {internal_token}"}
    file_content = b"test content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    form_data = {"document_type": DocumentType.MISCELLANEOUS.value}

    response = await ac.post(
        "/api/documents/create/1", headers=headers, files=files, data=form_data
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Document créé avec succès"}
