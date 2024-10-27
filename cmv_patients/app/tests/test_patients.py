import pytest


@pytest.mark.asyncio
async def test_get_patients_no_cookie(ac, patients):
    response = await ac.get("/api/patients/")
    print(f"RESPONSE : {response.status_code} {response.json()}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_patients_wrong_token(ac, wrong_internal_token, patients):
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/patients/", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_pagination_limit(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/?limit=5", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 20
    assert len(result["data"]) == 5


@pytest.mark.asyncio
async def test_pagination_offset(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/?limit=5&page=2", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 20
    assert len(result["data"]) == 5
    assert result["data"][0]["id_patient"] == 14


@pytest.mark.asyncio
async def test_pagination_tri_prenom_desc(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(
        "/api/patients/?limit=5&page=2&order=desc&field=prenom", headers=headers
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 20
    assert len(result["data"]) == 5
    assert result["data"][0]["prenom"] == "prenom_test_4"


@pytest.mark.asyncio
async def test_pagination_bad_type_page(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(
        "/api/patients/?limit=5&page=toto&order=desc&field=prenom", headers=headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_bad_type_limit(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(
        "/api/patients/?limit=toto&page=1&order=desc&field=prenom", headers=headers
    )

    assert response.status_code == 422
