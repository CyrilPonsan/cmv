from fastapi import Request
import pytest

from app.routers.patients import read_patients


@pytest.mark.asyncio
async def test_read_patients(mock_httpx_client, mock_dynamic_permissions, mocker):
    # Simuler l'objet Request avec des cookies
    mock_request = mocker.Mock(spec=Request)
    mock_request.cookies = {"session": "mocked_cookie_value"}

    # Appeler la fonction qui gère l'endpoint
    path = "test-path"
    result = await read_patients(
        path=path, current_user="mocked_user", request=mock_request
    )

    # Vérifier que le mock de read_patients a été appelé avec l'URL correcte et les cookies
    mock_httpx_client.read_patients.assert_called_once_with(
        f"http://your_patient_service_url/{path}/", {"session": "mocked_cookie_value"}
    )

    # Vérifier le résultat
    assert result == {"data": "mocked_data"}
