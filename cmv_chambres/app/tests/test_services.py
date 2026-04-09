"""Tests pour les endpoints /api/services — auth et lecture."""

import pytest


# ---- GET /api/services/simple (auth requise) ----


@pytest.mark.asyncio
async def test_get_simple_services_no_token(ac, services_and_chambres):
    """Sans token → 401."""
    response = await ac.get("/api/services/simple")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_simple_services(ac, internal_token, services_and_chambres):
    """Token valide → 200."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/services/simple", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nom"] == "Cardiologie"


# ---- GET /api/services/{service_id} (auth requise) ----


@pytest.mark.asyncio
async def test_get_all_services_no_token(ac, services_and_chambres):
    """Sans token → 401."""
    response = await ac.get("/api/services/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_services_wrong_token(ac, wrong_internal_token, services_and_chambres):
    """Mauvais token → 403."""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/services/1", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_services_bad_source(ac, bad_source_token, services_and_chambres):
    """Source non autorisée → 403."""
    headers = {"Authorization": f"Bearer {bad_source_token}"}
    response = await ac.get("/api/services/1", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_services_success(ac, internal_token, services_and_chambres):
    """Token valide → 200 avec service et chambres."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Use the id of the first service from fixtures
    service_id = services_and_chambres["services"][0].id_service
    response = await ac.get(f"/api/services/{service_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert len(data[0]["chambres"]) >= 1
