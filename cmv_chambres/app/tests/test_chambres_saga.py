"""Tests Saga côté Chambres (participant) — réservation et annulation.

Ce fichier contient les tests unitaires et property-based pour valider
le comportement de ChambresService lors des opérations de réservation
et d'annulation de chambres, appelées par l'orchestrateur (service admissions).
"""

from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from hypothesis import given, settings, strategies as st, HealthCheck

from app.repositories.chambres_crud import PgChambresRepository
from app.schemas.reservation import CreateReservation, ReservationResponse
from app.services.chambres import ChambresService
from app.sql.models import Chambre, Reservation, Service, Status


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

valid_datetimes = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31),
)

valid_reservation_data = st.builds(
    CreateReservation,
    patient_id=st.integers(min_value=1, max_value=10_000),
    entree_prevue=valid_datetimes,
    sortie_prevue=valid_datetimes,
)

nonexistent_service_ids = st.integers(min_value=9000, max_value=99_999)

nonexistent_chambre_ids = st.integers(min_value=9000, max_value=99_999)

nonexistent_reservation_ids = st.integers(min_value=9000, max_value=99_999)

non_libre_statuses = st.sampled_from([Status.OCCUPEE, Status.NETTOYAGE])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def chambres_service():
    """ChambresService avec un PgChambresRepository réel."""
    return ChambresService(PgChambresRepository())


@pytest.fixture
def service_with_free_room(db_session):
    """Service hospitalier avec une chambre LIBRE."""
    service = Service(nom="TestService")
    db_session.add(service)
    db_session.flush()
    chambre = Chambre(
        nom=f"T{service.id_service}01",
        status=Status.LIBRE,
        dernier_nettoyage=datetime.now(),
        service_id=service.id_service,
    )
    db_session.add(chambre)
    db_session.commit()
    return {"service": service, "chambre": chambre}


@pytest.fixture
def service_all_occupied(db_session):
    """Service hospitalier sans chambre LIBRE (toutes OCCUPEE)."""
    service = Service(nom="ServiceComplet")
    db_session.add(service)
    db_session.flush()
    for i in range(3):
        db_session.add(
            Chambre(
                nom=f"OCC{service.id_service}{i}",
                status=Status.OCCUPEE,
                dernier_nettoyage=datetime.now(),
                service_id=service.id_service,
            )
        )
    db_session.commit()
    return service


@pytest.fixture
def reservation_in_db(db_session, service_with_free_room):
    """Réservation pré-insérée avec chambre passée à OCCUPEE."""
    chambre = service_with_free_room["chambre"]
    chambre.status = Status.OCCUPEE
    reservation = Reservation(
        chambre_id=chambre.id_chambre,
        ref=1,
        entree_prevue=datetime.now(),
        sortie_prevue=datetime.now() + timedelta(days=3),
    )
    db_session.add(reservation)
    db_session.commit()
    return {"reservation": reservation, "chambre": chambre}


# ---------------------------------------------------------------------------
# 2.1 — Tests unitaires de réservation (via AsyncClient / routeur)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reservation_success_returns_201(
    ac, internal_token, services_and_chambres
):
    """Validates: Requirements 1.3 — réservation réussie retourne 201 avec ReservationResponse."""
    service = services_and_chambres["services"][0]  # Cardiologie, has a LIBRE room
    body = {
        "patient_id": 42,
        "entree_prevue": "2026-06-01T10:00:00",
        "sortie_prevue": "2026-06-05T10:00:00",
    }

    resp = await ac.post(
        f"/api/chambres/{service.id_service}/reserver",
        json=body,
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert "reservation_id" in data
    assert "chambre_id" in data
    assert "sortie_prevue_le" in data
    # The returned sortie_prevue_le must match the submitted sortie_prevue
    assert data["sortie_prevue_le"] == "2026-06-05T10:00:00"


@pytest.mark.asyncio
async def test_reservation_no_room_returns_404(
    ac, internal_token, service_all_occupied
):
    """Validates: Requirements 2.1 — aucune chambre LIBRE → 404 no_room_available."""
    body = {
        "patient_id": 1,
        "entree_prevue": "2026-06-01T10:00:00",
        "sortie_prevue": "2026-06-05T10:00:00",
    }

    resp = await ac.post(
        f"/api/chambres/{service_all_occupied.id_service}/reserver",
        json=body,
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "no_room_available"


@pytest.mark.asyncio
async def test_reservation_nonexistent_service_returns_404(ac, internal_token):
    """Validates: Requirements 3.1 — service_id inexistant → 404 no_room_available."""
    body = {
        "patient_id": 1,
        "entree_prevue": "2026-06-01T10:00:00",
        "sortie_prevue": "2026-06-05T10:00:00",
    }

    resp = await ac.post(
        "/api/chambres/99999/reserver",
        json=body,
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "no_room_available"


# ---------------------------------------------------------------------------
# 2.2 — Test property-based : round-trip réservation
# ---------------------------------------------------------------------------

import asyncio
import uuid


# Feature: chambres-saga-tests, Property 1: Round-trip réservation
@given(data=valid_reservation_data)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_reservation_roundtrip(db_session, data):
    """**Validates: Requirements 1.1, 1.2, 1.3**

    Pour toute CreateReservation valide et tout Service contenant au moins
    une Chambre LIBRE, post_reservation doit :
    - créer une Reservation en base avec ref == patient_id, entree_prevue et
      sortie_prevue correspondant aux données soumises
    - mettre à jour le statut de la Chambre réservée à OCCUPEE
    - retourner une ReservationResponse avec reservation_id valide, chambre_id
      de la chambre réservée et sortie_prevue_le == sortie_prevue
    """
    service = ChambresService(PgChambresRepository())

    # --- setup: service + chambre LIBRE unique par exemple ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambre = Chambre(
        nom=f"CH_{uuid.uuid4().hex[:12]}",
        status=Status.LIBRE,
        dernier_nettoyage=datetime.now(),
        service_id=svc.id_service,
    )
    db_session.add(chambre)
    db_session.commit()

    chambre_id_before = chambre.id_chambre

    # --- act ---
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(
        service.post_reservation(db_session, svc.id_service, data)
    )

    # --- assert 1: ReservationResponse fields ---
    assert isinstance(response, ReservationResponse)
    assert response.reservation_id is not None and response.reservation_id > 0
    assert response.chambre_id == chambre_id_before
    assert response.sortie_prevue_le == data.sortie_prevue

    # --- assert 2: Reservation persisted in DB with correct fields ---
    reservation_db = (
        db_session.query(Reservation)
        .filter(Reservation.id_reservation == response.reservation_id)
        .first()
    )
    assert reservation_db is not None
    assert reservation_db.ref == data.patient_id
    assert reservation_db.entree_prevue == data.entree_prevue
    assert reservation_db.sortie_prevue == data.sortie_prevue

    # --- assert 3: Chambre status updated to OCCUPEE ---
    db_session.refresh(chambre)
    assert chambre.status == Status.OCCUPEE

    # --- cleanup: remove reservation and reset chambre for next example ---
    db_session.delete(reservation_db)
    chambre.status = Status.LIBRE
    db_session.commit()


# Feature: chambres-saga-tests, Property 2: Aucune chambre disponible
@given(data=valid_reservation_data, room_status=non_libre_statuses)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_no_room_prevents_reservation(db_session, data, room_status):
    """**Validates: Requirements 2.1, 2.2, 2.3**

    Pour tout Service_Hospitalier dont toutes les Chambres ont un statut
    différent de LIBRE (OCCUPEE ou NETTOYAGE), et pour toute CreateReservation
    valide, post_reservation doit :
    - lever une HTTPException(404, "no_room_available")
    - ne créer aucune Reservation en base
    - ne modifier le statut d'aucune Chambre
    """
    service = ChambresService(PgChambresRepository())

    # --- setup: service + chambres all non-LIBRE ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambres = []
    for i in range(3):
        ch = Chambre(
            nom=f"CH_{uuid.uuid4().hex[:12]}",
            status=room_status,
            dernier_nettoyage=datetime.now(),
            service_id=svc.id_service,
        )
        db_session.add(ch)
        chambres.append(ch)
    db_session.commit()

    # Record statuses before
    statuses_before = {ch.id_chambre: ch.status for ch in chambres}

    # Count reservations before
    reservations_before = db_session.query(Reservation).count()

    # --- act: expect HTTPException 404 ---
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as exc_info:
        loop.run_until_complete(
            service.post_reservation(db_session, svc.id_service, data)
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "no_room_available"

    # --- assert: no Reservation created ---
    reservations_after = db_session.query(Reservation).count()
    assert reservations_after == reservations_before

    # --- assert: no Chambre status changed ---
    for ch in chambres:
        db_session.refresh(ch)
        assert ch.status == statuses_before[ch.id_chambre]

    # --- cleanup ---
    for ch in chambres:
        db_session.delete(ch)
    db_session.delete(svc)
    db_session.commit()


# Feature: chambres-saga-tests, Property 3: Service inexistant
@given(data=valid_reservation_data, fake_service_id=nonexistent_service_ids)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_nonexistent_service_prevents_reservation(db_session, data, fake_service_id):
    """**Validates: Requirements 3.1, 3.2**

    Pour tout service_id ne correspondant à aucun Service_Hospitalier en base,
    et pour toute CreateReservation valide, post_reservation doit :
    - lever une HTTPException(404, "no_room_available")
    - ne créer aucune Reservation en base
    """
    service = ChambresService(PgChambresRepository())

    # Count reservations before
    reservations_before = db_session.query(Reservation).count()

    # --- act: expect HTTPException 404 ---
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as exc_info:
        loop.run_until_complete(
            service.post_reservation(db_session, fake_service_id, data)
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "no_room_available"

    # --- assert: no Reservation created ---
    reservations_after = db_session.query(Reservation).count()
    assert reservations_after == reservations_before


# ---------------------------------------------------------------------------
# 3.1 — Tests unitaires d'annulation (via AsyncClient / routeur)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_success_returns_200(ac, reservation_in_db, db_session):
    """Validates: Requirements 4.3, 5.1 — annulation réussie retourne 200, supprime la réservation et libère la chambre."""
    reservation = reservation_in_db["reservation"]
    chambre = reservation_in_db["chambre"]
    reservation_id = reservation.id_reservation
    chambre_id = chambre.id_chambre

    resp = await ac.delete(
        f"/api/chambres/{reservation_id}/{chambre_id}/cancel",
    )

    assert resp.status_code == 200

    # Verify the reservation is deleted from the DB
    deleted = db_session.query(Reservation).filter(
        Reservation.id_reservation == reservation_id
    ).first()
    assert deleted is None

    # Verify the chambre status is back to LIBRE
    updated_chambre = db_session.query(Chambre).filter(
        Chambre.id_chambre == chambre_id
    ).first()
    assert updated_chambre.status == Status.LIBRE


@pytest.mark.asyncio
async def test_cancel_chambre_not_found_returns_404(ac, reservation_in_db):
    """Validates: Requirements 5.1 — chambre_id inexistant → 404 chambre_not_found."""
    reservation = reservation_in_db["reservation"]

    resp = await ac.delete(
        f"/api/chambres/{reservation.id_reservation}/99999/cancel",
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "chambre_not_found"


@pytest.mark.asyncio
async def test_cancel_reservation_not_found_returns_404(
    ac, service_with_free_room, db_session
):
    """Validates: Requirements 6.1, 6.2 — reservation_id inexistant → 404 reservation_not_found, chambre libérée."""
    chambre = service_with_free_room["chambre"]
    chambre_id = chambre.id_chambre
    # Set chambre to OCCUPEE so we can verify it gets freed
    chambre.status = Status.OCCUPEE
    db_session.commit()

    resp = await ac.delete(
        f"/api/chambres/99999/{chambre_id}/cancel",
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "reservation_not_found"

    # Verify the chambre is still freed to LIBRE despite the error
    updated_chambre = db_session.query(Chambre).filter(
        Chambre.id_chambre == chambre_id
    ).first()
    assert updated_chambre.status == Status.LIBRE


# ---------------------------------------------------------------------------
# 3.2 — Test property-based : annulation nominale
# ---------------------------------------------------------------------------

# Feature: chambres-saga-tests, Property 4: Annulation nominale
@given(data=valid_reservation_data)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_cancel_deletes_and_frees(db_session, data):
    """**Validates: Requirements 4.1, 4.2**

    Pour toute Reservation existante en base avec une Chambre associée au
    statut OCCUPEE, cancel_reservation avec le reservation_id et chambre_id
    valides doit :
    - supprimer la Reservation de la base de données
    - mettre à jour le statut de la Chambre à LIBRE
    """
    service = ChambresService(PgChambresRepository())
    loop = asyncio.get_event_loop()

    # --- setup: service + chambre LIBRE unique par exemple ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambre = Chambre(
        nom=f"CH_{uuid.uuid4().hex[:12]}",
        status=Status.LIBRE,
        dernier_nettoyage=datetime.now(),
        service_id=svc.id_service,
    )
    db_session.add(chambre)
    db_session.commit()

    # --- create reservation (sets chambre to OCCUPEE) ---
    response = loop.run_until_complete(
        service.post_reservation(db_session, svc.id_service, data)
    )
    reservation_id = response.reservation_id
    chambre_id = response.chambre_id

    # Verify preconditions: chambre is OCCUPEE and reservation exists
    db_session.refresh(chambre)
    assert chambre.status == Status.OCCUPEE

    # --- act: cancel the reservation ---
    result = loop.run_until_complete(
        service.cancel_reservation(db_session, reservation_id, chambre_id)
    )

    # --- assert 1: Reservation deleted from DB ---
    deleted = (
        db_session.query(Reservation)
        .filter(Reservation.id_reservation == reservation_id)
        .first()
    )
    assert deleted is None

    # --- assert 2: Chambre status updated to LIBRE ---
    db_session.refresh(chambre)
    assert chambre.status == Status.LIBRE

    # --- cleanup ---
    db_session.delete(chambre)
    db_session.delete(svc)
    db_session.commit()


# ---------------------------------------------------------------------------
# 3.3 — Test property-based : chambre introuvable empêche l'annulation
# ---------------------------------------------------------------------------

# Feature: chambres-saga-tests, Property 5: Chambre introuvable
@given(
    fake_chambre_id=nonexistent_chambre_ids,
    fake_reservation_id=nonexistent_reservation_ids,
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_cancel_nonexistent_chambre(db_session, fake_chambre_id, fake_reservation_id):
    """**Validates: Requirements 5.1, 5.2**

    Pour tout chambre_id ne correspondant à aucune Chambre en base,
    cancel_reservation doit :
    - lever une HTTPException(404, "chambre_not_found")
    - ne supprimer aucune Reservation
    """
    service = ChambresService(PgChambresRepository())
    loop = asyncio.get_event_loop()

    # Count reservations before
    reservations_before = db_session.query(Reservation).count()

    # --- act: expect HTTPException 404 ---
    with pytest.raises(HTTPException) as exc_info:
        loop.run_until_complete(
            service.cancel_reservation(db_session, fake_reservation_id, fake_chambre_id)
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "chambre_not_found"

    # --- assert: no Reservation deleted ---
    reservations_after = db_session.query(Reservation).count()
    assert reservations_after == reservations_before


# ---------------------------------------------------------------------------
# 3.4 — Test property-based : réservation introuvable libère la chambre
# ---------------------------------------------------------------------------

# Feature: chambres-saga-tests, Property 6: Réservation introuvable
@given(fake_reservation_id=nonexistent_reservation_ids)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_cancel_nonexistent_reservation_frees_room(db_session, fake_reservation_id):
    """**Validates: Requirements 6.1, 6.2**

    Pour tout chambre_id valide correspondant à une Chambre existante et tout
    reservation_id ne correspondant à aucune Reservation, cancel_reservation doit :
    - mettre à jour le statut de la Chambre à LIBRE
    - puis lever une HTTPException(404, "reservation_not_found")
    """
    service = ChambresService(PgChambresRepository())
    loop = asyncio.get_event_loop()

    # --- setup: service + chambre OCCUPEE ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambre = Chambre(
        nom=f"CH_{uuid.uuid4().hex[:12]}",
        status=Status.OCCUPEE,
        dernier_nettoyage=datetime.now(),
        service_id=svc.id_service,
    )
    db_session.add(chambre)
    db_session.commit()

    chambre_id = chambre.id_chambre

    # --- act: cancel with nonexistent reservation_id but valid chambre_id ---
    with pytest.raises(HTTPException) as exc_info:
        loop.run_until_complete(
            service.cancel_reservation(db_session, fake_reservation_id, chambre_id)
        )

    # --- assert 1: HTTPException 404 reservation_not_found ---
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "reservation_not_found"

    # --- assert 2: Chambre status updated to LIBRE despite the error ---
    db_session.refresh(chambre)
    assert chambre.status == Status.LIBRE

    # --- cleanup ---
    db_session.delete(chambre)
    db_session.delete(svc)
    db_session.commit()


# ---------------------------------------------------------------------------
# 5.1 — Test property-based : round-trip réservation → annulation
# ---------------------------------------------------------------------------

# Feature: chambres-saga-tests, Property 7: Round-trip réservation → annulation
@given(data=valid_reservation_data)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_reserve_then_cancel_roundtrip(db_session, data):
    """**Validates: Requirements 7.1, 7.2, 7.3**

    Pour toute CreateReservation valide et tout Service_Hospitalier contenant
    une Chambre LIBRE, le cycle complet (réserver puis annuler) doit :
    - remettre le statut de la Chambre à LIBRE
    - supprimer la Reservation de la base de données
    - laisser le nombre total de Reservations en base identique au nombre initial
    """
    service = ChambresService(PgChambresRepository())
    loop = asyncio.get_event_loop()

    # --- setup: service + chambre LIBRE unique par exemple ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambre = Chambre(
        nom=f"CH_{uuid.uuid4().hex[:12]}",
        status=Status.LIBRE,
        dernier_nettoyage=datetime.now(),
        service_id=svc.id_service,
    )
    db_session.add(chambre)
    db_session.commit()

    # Count initial reservations
    initial_reservation_count = db_session.query(Reservation).count()

    # --- act 1: reserve ---
    response = loop.run_until_complete(
        service.post_reservation(db_session, svc.id_service, data)
    )
    reservation_id = response.reservation_id
    chambre_id = response.chambre_id

    # Verify reservation was created (precondition)
    db_session.refresh(chambre)
    assert chambre.status == Status.OCCUPEE

    # --- act 2: cancel ---
    loop.run_until_complete(
        service.cancel_reservation(db_session, reservation_id, chambre_id)
    )

    # --- assert 1: Chambre status back to LIBRE ---
    db_session.refresh(chambre)
    assert chambre.status == Status.LIBRE

    # --- assert 2: Reservation deleted from DB ---
    deleted = (
        db_session.query(Reservation)
        .filter(Reservation.id_reservation == reservation_id)
        .first()
    )
    assert deleted is None

    # --- assert 3: Total reservation count unchanged ---
    final_reservation_count = db_session.query(Reservation).count()
    assert final_reservation_count == initial_reservation_count

    # --- cleanup ---
    db_session.delete(chambre)
    db_session.delete(svc)
    db_session.commit()


# ---------------------------------------------------------------------------
# 5.2 — Test property-based : sélection de chambre disponible
# ---------------------------------------------------------------------------

# Feature: chambres-saga-tests, Property 8: Sélection de chambre disponible
@given(
    statuses=st.lists(
        st.sampled_from([Status.LIBRE, Status.OCCUPEE, Status.NETTOYAGE]),
        min_size=1,
        max_size=5,
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prop_available_room_selection(db_session, statuses):
    """**Validates: Requirements 8.1, 8.2, 8.3**

    Pour tout Service_Hospitalier contenant au moins une Chambre LIBRE,
    get_available_room doit retourner exactement une Chambre avec le statut
    LIBRE appartenant à ce service.
    Pour tout Service_Hospitalier dont toutes les Chambres sont OCCUPEE ou
    NETTOYAGE, get_available_room doit lever une HTTPException(404,
    "no_room_available").
    """
    service = ChambresService(PgChambresRepository())
    loop = asyncio.get_event_loop()

    has_libre = any(s == Status.LIBRE for s in statuses)

    # --- setup: service + chambres with generated statuses ---
    svc = Service(nom=f"Svc_{uuid.uuid4().hex[:8]}")
    db_session.add(svc)
    db_session.flush()

    chambres = []
    for s in statuses:
        ch = Chambre(
            nom=f"CH_{uuid.uuid4().hex[:12]}",
            status=s,
            dernier_nettoyage=datetime.now(),
            service_id=svc.id_service,
        )
        db_session.add(ch)
        chambres.append(ch)
    db_session.commit()

    if has_libre:
        # --- case 1: at least one LIBRE room exists ---
        result = loop.run_until_complete(
            service.get_available_room(db_session, svc.id_service)
        )

        # returned exactly one Chambre with status LIBRE belonging to this service
        assert isinstance(result, Chambre)
        assert result.status == Status.LIBRE
        assert result.service_id == svc.id_service
    else:
        # --- case 2: all rooms are OCCUPEE or NETTOYAGE ---
        with pytest.raises(HTTPException) as exc_info:
            loop.run_until_complete(
                service.get_available_room(db_session, svc.id_service)
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "no_room_available"

    # --- cleanup ---
    for ch in chambres:
        db_session.delete(ch)
    db_session.delete(svc)
    db_session.commit()


# ---------------------------------------------------------------------------
# 6.1 — Tests de validation Pydantic (via AsyncClient / routeur)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reservation_missing_fields_returns_422(ac, internal_token):
    """Validates: Requirements 9.1 — champs requis absents → HTTP 422."""
    resp = await ac.post(
        "/api/chambres/1/reserver",
        json={},
        headers={"Authorization": f"Bearer {internal_token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_reservation_invalid_datetime_returns_422(ac, internal_token):
    """Validates: Requirements 9.2 — types datetime invalides → HTTP 422."""
    resp = await ac.post(
        "/api/chambres/1/reserver",
        json={
            "patient_id": 1,
            "entree_prevue": "not-a-datetime",
            "sortie_prevue": "also-not-a-datetime",
        },
        headers={"Authorization": f"Bearer {internal_token}"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 6.2 — Tests d'authentification JWT
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reservation_no_token_returns_401(ac):
    """Validates: Requirements 10.1 — requête sans token JWT → HTTP 401 Not authenticated."""
    resp = await ac.post(
        "/api/chambres/1/reserver",
        json={
            "patient_id": 1,
            "entree_prevue": "2026-06-01T10:00:00",
            "sortie_prevue": "2026-06-05T10:00:00",
        },
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_reservation_invalid_token_returns_403(ac):
    """Validates: Requirements 10.2 — token JWT invalide → HTTP 403 not_authorized."""
    resp = await ac.post(
        "/api/chambres/1/reserver",
        json={
            "patient_id": 1,
            "entree_prevue": "2026-06-01T10:00:00",
            "sortie_prevue": "2026-06-05T10:00:00",
        },
        headers={"Authorization": "Bearer invalid.garbage.token"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "not_authorized"


@pytest.mark.asyncio
async def test_reservation_valid_sources_accepted(
    ac, internal_token, patients_token, services_and_chambres
):
    """Validates: Requirements 10.3 — sources api_patients et api_gateway sont acceptées."""
    service_id = services_and_chambres["services"][0].id_service
    body = {
        "patient_id": 100,
        "entree_prevue": "2026-07-01T10:00:00",
        "sortie_prevue": "2026-07-05T10:00:00",
    }

    # api_gateway source (internal_token)
    resp_gw = await ac.post(
        f"/api/chambres/{service_id}/reserver",
        json=body,
        headers={"Authorization": f"Bearer {internal_token}"},
    )
    assert resp_gw.status_code != 401
    assert resp_gw.status_code != 403

    # api_patients source (patients_token)
    resp_pt = await ac.post(
        f"/api/chambres/{service_id}/reserver",
        json=body,
        headers={"Authorization": f"Bearer {patients_token}"},
    )
    assert resp_pt.status_code != 401
    assert resp_pt.status_code != 403
