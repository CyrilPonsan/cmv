"""Tests pour les endpoints /api/services — auth et lecture."""

import pytest


# ---- GET /api/services/simple (pas d'auth) ----


@pytest.mark.asyncio
async def test_get_simple_services(ac, services_and_chambres):
    """Liste simplifiée des services, pas d'auth requise."""
    response = await ac.get("/api/services/simple")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nom"] == "Cardiologie"


# ---- GET /api/services/ (auth requise) ----


@pytest.mark.asyncio
async def test_get_all_services_no_token(ac, services_and_chambres):
    """Sans token → 401."""
    response = await ac.get("/api/services/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_services_wrong_token(ac, wrong_internal_token, services_and_chambres):
    """Mauvais token → 403."""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/services/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_services_success(ac, internal_token, services_and_chambres):
    """Token valide → 200 avec services et chambres."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/services/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Chaque service doit avoir ses chambres
    assert len(data[0]["chambres"]) >= 1
