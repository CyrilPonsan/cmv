import pytest
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_get_patients(
    ac, auth_cookie, mock_patients_service, httpx_mock: HTTPXMock
):
    # Mock le micro service
    httpx_mock.add_response(
        url="http://mock-patients-service/foo",
        json={"message": "Test réussi !"},
        status_code=200,
    )

    headers = {"Cookie": f"access_token={auth_cookie}"}
    response = await ac.get("/api/patients/foo", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Test réussi !"}


@pytest.mark.asyncio
async def test_get_patients_not_found(
    ac, auth_cookie, mock_patients_service, httpx_mock: HTTPXMock
):
    # Mock le micro service
    httpx_mock.add_response(
        url="http://mock-patients-service/foo",
        json={"detail": "Not Found"},
        status_code=404,
    )

    headers = {"Cookie": f"access_token={auth_cookie}"}
    response = await ac.get("/api/patients/foo", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_get_patients_no_cookie(ac):
    response = await ac.get("/api/patients/foo")

    print(f"RESPONSE : {response.json()}")

    assert response.status_code == 401
    assert response.json() == {"detail": "not_authenticated"}
