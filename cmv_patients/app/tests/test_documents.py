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
    file_content = b"%PDF-1.4 test content"
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
        "app.services.patients.PatientsService._upload_file_to_s3", return_value=True
    )

    headers = {"Authorization": f"Bearer {internal_token}"}
    file_content = b"%PDF-1.4 test content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    form_data = {"document_type": DocumentType.MISCELLANEOUS.value}

    response = await ac.post(
        "/api/documents/create/1", headers=headers, files=files, data=form_data
    )

    assert response.status_code == 200
    assert response.json() == {"message": "document_created", "success": True}


@pytest.mark.asyncio
async def test_delete_document_no_auth(ac):
    """Test la suppression d'un document sans authentification"""
    response = await ac.delete("/api/documents/delete/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_delete_document_wrong_token(ac, wrong_internal_token):
    """Test la suppression d'un document avec un token invalide"""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.delete("/api/documents/delete/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_delete_document_not_found(ac, internal_token):
    """Test la suppression d'un document inexistant"""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.delete("/api/documents/delete/999", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "document_not_found"}


@pytest.mark.asyncio
async def test_delete_document_success(ac, internal_token, patients, mocker):
    """Test la suppression réussie d'un document"""
    # Mock de la suppression S3
    mocker.patch(
        "app.services.patients.PatientsService.delete_document_by_id",
        return_value={
            "success": True,
            "message": "document_deleted",
        },
    )

    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.delete("/api/documents/delete/1", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "document_deleted",
    }


@pytest.mark.asyncio
async def test_download_document_no_auth(ac):
    """Test le téléchargement d'un document sans authentification"""
    response = await ac.get("/api/documents/download/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_download_document_wrong_token(ac, wrong_internal_token):
    """Test le téléchargement d'un document avec un token invalide"""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/documents/download/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_download_document_not_found(ac, internal_token):
    """Test le téléchargement d'un document inexistant"""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/documents/download/999", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "document_not_found"}


@pytest.mark.asyncio
async def test_download_document_success(ac, internal_token, patients, mocker):
    """Test le téléchargement réussi d'un document"""
    test_content = b"%PDF-1.4 test content"
    mock_file = BytesIO(test_content)
    mock_file.seek(0)

    mocker.patch(
        "app.services.patients.PatientsService.download_file_from_s3",
        return_value=(mock_file, "test.pdf"),
    )

    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/documents/download/1", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == 'inline; filename="test.pdf"'
    content = response.content  # Utiliser .content au lieu de await response.read()
    assert content == test_content
