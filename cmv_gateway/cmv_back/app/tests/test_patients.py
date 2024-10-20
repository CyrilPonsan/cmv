from httpx import AsyncClient
import pytest
from pytest_httpx import HTTPXMock

from app.services.patients import PatientsService


@pytest.mark.asyncio
async def test_get_patients(
    ac, auth_cookie, mock_patients_service: PatientsService, httpx_mock: HTTPXMock
):
    # Mock the external service call
    httpx_mock.add_response(
        url="http://localhost:8002",
        json={"message": "Test réussi !"},
        status_code=200,
    )

    headers = {"Cookie": f"access_token={auth_cookie}"}
    response = await ac.get("/api/patients/foo", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Test réussi !"}

    # Verify that the mock was called
    request = httpx_mock.get_request()
    assert request.url == "http://mock-patients-service/foo/"
    assert "Cookie" in request.headers
    assert f"access_token={auth_cookie}" in request.headers["Cookie"]
