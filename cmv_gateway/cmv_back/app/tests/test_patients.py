from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_read_patients(ac, auth_cookie, mock_dynamic_permissions, mocker):
    # Créer un mock pour httpx.AsyncClient
    mock_httpx_client = AsyncMock()

    # Mock la réponse du service pour la méthode get
    mock_httpx_client.get.return_value.json.return_value = {"data": "mocked_data"}
    mock_httpx_client.get.return_value.status_code = 200

    # Patch la dépendance get_http_client pour renvoyer le mock
    mocker.patch(
        "app.dependancies.httpx_client.get_http_client", return_value=mock_httpx_client
    )

    # Préparer les en-têtes avec le cookie d'authentification
    headers = {"Cookie": f"access_token={auth_cookie}"}

    # Appeler le point de terminaison API
    response = await ac.get("/api/patients/foo", headers=headers)

    # Vérifie que la réponse est correcte
    assert response.status_code == 200
    assert response.json() == {"data": "mocked_data"}
