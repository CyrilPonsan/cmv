"""Tests pour les endpoints /api/chambres — auth, get available room, validation."""

import pytest


# ---- Auth : pas de token ----


@pytest.mark.asyncio
async def test_get_chambre_no_token(ac, services_and_chambres):
    """Sans token, la route doit retourner 401."""
    response = await ac.get("/api/chambres/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_chambre_wrong_token(ac, wrong_internal_token, services_and_chambres):
    """Avec un token signé avec la mauvaise clé, 403."""
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.get("/api/chambres/1", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "not_authorized"}


# ---- GET chambre disponible ----


@pytest.mark.asyncio
async def test_get_available_room_success(ac, internal_token, services_and_chambres):
    """Récupère une chambre libre dans un service qui en a."""
    service_id = services_and_chambres["services"][0].id_service
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(f"/api/chambres/{service_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "C101"
    assert data["service_id"] == service_id


@pytest.mark.asyncio
async def test_get_available_room_none_available(ac, internal_token, db_session, services_and_chambres):
    """Quand toutes les chambres sont occupées, 404."""
    from app.sql.models import Chambre, Status

    # Passer toutes les chambres du service 1 en occupées
    db_session.query(Chambre).filter(
        Chambre.service_id == services_and_chambres["services"][0].id_service
    ).update({"status": Status.OCCUPEE})
    db_session.commit()

    service_id = services_and_chambres["services"][0].id_service
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get(f"/api/chambres/{service_id}", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "no_room_available"}


@pytest.mark.asyncio
async def test_get_available_room_nonexistent_service(ac, internal_token, services_and_chambres):
    """Service inexistant → 404 (pas de chambre libre)."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/chambres/999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_available_room_invalid_service_id(ac, internal_token):
    """service_id non-entier → 422 validation error."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.get("/api/chambres/abc", headers=headers)
    assert response.status_code == 422


# ---- PUT update chambre status ----


@pytest.mark.asyncio
async def test_update_chambre_no_token(ac, services_and_chambres):
    """PUT sans token → 401."""
    chambre_id = services_and_chambres["chambres"][0].id_chambre
    response = await ac.put(f"/api/chambres/{chambre_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_chambre_wrong_token(ac, wrong_internal_token, services_and_chambres):
    """PUT avec mauvais token → 403."""
    chambre_id = services_and_chambres["chambres"][0].id_chambre
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    response = await ac.put(f"/api/chambres/{chambre_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_chambre_success(ac, internal_token, services_and_chambres):
    """PUT avec token valide → 200 + chambre mise à jour."""
    chambre_id = services_and_chambres["chambres"][1].id_chambre  # occupée
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.put(f"/api/chambres/{chambre_id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Chambre mise à jour"}


@pytest.mark.asyncio
async def test_update_chambre_not_found(ac, internal_token, services_and_chambres):
    """PUT sur chambre inexistante → 404."""
    headers = {"Authorization": f"Bearer {internal_token}"}
    response = await ac.put("/api/chambres/999", headers=headers)
    assert response.status_code == 404
