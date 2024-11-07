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
    assert result["total"] == 21
    assert len(result["data"]) == 5


@pytest.mark.asyncio
async def test_pagination_offset(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/?limit=5&page=2", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 21
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
    assert result["total"] == 21
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


@pytest.mark.asyncio
async def test_pagination_tri_nom_asc(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(
        "/api/patients/?limit=5&page=1&order=asc&field=nom", headers=headers
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 5
    assert result["data"][0]["nom"] == "nom_test_0"


@pytest.mark.asyncio
async def test_pagination_limit_extreme(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/?limit=1000", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 21


@pytest.mark.asyncio
async def test_search_patients(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/search?search=toto", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 1
    assert result["data"][0]["nom"] == "toto"


@pytest.mark.asyncio
async def test_search_mass_patients(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/search?search=test", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 20
    assert len(result["data"]) == 10
    assert result["data"][0]["nom"] == "nom_test_0"


@pytest.mark.asyncio
async def test_no_data_found_from_search(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/search?search=blabla", headers=headers)

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 0
    assert len(result["data"]) == 0
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_patient_detail_no_cookie(ac, patients):
    response = await ac.get("/api/patients/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_patient_detail_wrong_token(ac, wrong_internal_token, patients):
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/patients/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_get_patient_detail_not_found(ac, internal_token):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/999", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "patient_not_found"}


@pytest.mark.asyncio
async def test_get_patient_detail_success(ac, internal_token, patients):
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/patients/1", headers=headers)
    result = response.json()

    assert response.status_code == 200
    assert result["id_patient"] == 1
    assert "nom" in result
    assert "prenom" in result
    assert "date_de_naissance" in result
    assert "adresse" in result
    assert "code_postal" in result
    assert "ville" in result
    assert "telephone" in result
    assert "email" in result
