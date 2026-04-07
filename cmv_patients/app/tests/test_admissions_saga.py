"""Tests du pattern Saga pour AdmissionService.

Tests unitaires et property-based (Hypothesis) validant la création/suppression
d'admissions, la gestion des erreurs et les mécanismes de compensation.
"""

from datetime import datetime
from unittest.mock import MagicMock

import httpx
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.schemas.patients import CreateAdmission
from app.services.admissions import AdmissionService
from app.sql.models import Admission, Patient
from app.utils.config import CHAMBRES_SERVICE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def admission_service():
    """Service avec repository réel."""
    return AdmissionService(admissions_repository=PgAdmissionsRepository())


@pytest.fixture
def mock_request():
    """Request factice avec headers IP."""
    request = MagicMock()
    request.headers = {"X-Real-IP": "127.0.0.1", "X-Forwarded-For": "127.0.0.1"}
    return request


@pytest.fixture
def patient_in_db(db_session):
    """Patient pré-inséré pour les tests d'admission."""
    patient = Patient(
        civilite="AUTRE",
        nom="test",
        prenom="patient",
        adresse="1 rue test",
        code_postal="64000",
        ville="Pau",
        telephone="0600000000",
        date_de_naissance=datetime(1990, 1, 1),
    )
    db_session.add(patient)
    db_session.commit()
    return patient


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

ambulatoire_admission = st.builds(
    CreateAdmission,
    patient_id=st.just(1),
    ambulatoire=st.just(True),
    entree_le=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    sortie_prevue_le=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    service_id=st.none(),
)

non_ambulatoire_admission = st.builds(
    CreateAdmission,
    patient_id=st.just(1),
    ambulatoire=st.just(False),
    entree_le=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    sortie_prevue_le=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    service_id=st.integers(min_value=1, max_value=100),
)

error_status_codes = st.integers(min_value=200, max_value=599).filter(lambda x: x != 201)

cancel_failure_codes = st.integers(min_value=200, max_value=599).filter(lambda x: x not in (200, 404))

reservation_ids = st.integers(min_value=1, max_value=10000)

chambre_ids = st.integers(min_value=1, max_value=500)


# ---------------------------------------------------------------------------
# 2.1 — Tests unitaires de création (erreurs réservation)
# ---------------------------------------------------------------------------


async def test_reservation_404_raises_no_room_available(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock
):
    """Validates: Requirements 3.1

    Quand le Service_Chambres retourne 404, create_admission lève
    HTTPException(404, 'no_room_available').
    """
    from fastapi import HTTPException

    data = CreateAdmission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        service_id=1,
    )

    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=404,
    )

    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "no_room_available"


async def test_reservation_500_raises_reservation_failed(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock
):
    """Validates: Requirements 3.2

    Quand le Service_Chambres retourne 500, create_admission lève
    HTTPException(500, 'reservation_failed').
    """
    from fastapi import HTTPException

    data = CreateAdmission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        service_id=1,
    )

    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=500,
    )

    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "reservation_failed"


# ---------------------------------------------------------------------------
# 2.2 — Test property-based : admission ambulatoire (round-trip)
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 1: Round-trip admission ambulatoire
@given(data=ambulatoire_admission)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_ambulatoire_roundtrip(
    data: CreateAdmission,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 1.1, 1.2, 1.3**

    Pour toute CreateAdmission ambulatoire, l'admission retournée doit avoir
    ref_reservation == None, ambulatoire == True, et les champs doivent
    correspondre aux données soumises. Aucun appel HTTP ne doit être émis.
    """
    # Override patient_id to match the patient actually in DB
    data = data.model_copy(update={"patient_id": patient_in_db.id_patient})

    admission = await admission_service.create_admission(
        db=db_session,
        data=data,
        internal_payload="fake-token",
        request=mock_request,
    )

    # Verify ref_reservation is None (no room reservation for ambulatoire)
    assert admission.ref_reservation is None
    # Verify ambulatoire flag
    assert admission.ambulatoire is True
    # Verify fields match submitted data
    assert admission.patient_id == data.patient_id
    assert admission.entree_le == data.entree_le
    assert admission.sortie_prevue_le == data.sortie_prevue_le
    # Verify no HTTP calls were made
    assert httpx_mock.get_requests() == []

    # Cleanup: remove the admission so next Hypothesis example starts clean
    db_session.delete(admission)
    db_session.commit()


# ---------------------------------------------------------------------------
# 2.3 — Test property-based : admission non ambulatoire (round-trip)
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 2: Round-trip admission non ambulatoire avec réservation
@given(
    data=non_ambulatoire_admission,
    reservation_id=reservation_ids,
    chambre_id=chambre_ids,
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_non_ambulatoire_roundtrip(
    data: CreateAdmission,
    reservation_id: int,
    chambre_id: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 2.1, 2.2, 2.3**

    Pour toute CreateAdmission non ambulatoire avec service_id valide,
    quand le Service_Chambres retourne 201 avec reservation_id et chambre_id,
    l'admission retournée doit avoir ref_reservation == reservation_id,
    ambulatoire == False, et les champs doivent correspondre aux données soumises.
    """
    # Override patient_id to match the patient actually in DB
    data = data.model_copy(update={"patient_id": patient_in_db.id_patient})

    # Mock the POST to Service_Chambres to return 201 with reservation data
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=201,
        json={"reservation_id": reservation_id, "chambre_id": chambre_id},
    )

    admission = await admission_service.create_admission(
        db=db_session,
        data=data,
        internal_payload="fake-token",
        request=mock_request,
    )

    # Verify ref_reservation matches the reservation_id from Service_Chambres
    assert admission.ref_reservation == reservation_id
    # Verify ambulatoire is False
    assert admission.ambulatoire is False
    # Verify fields match submitted data
    assert admission.patient_id == data.patient_id
    assert admission.entree_le == data.entree_le
    assert admission.sortie_prevue_le == data.sortie_prevue_le

    # Cleanup: remove the admission so next Hypothesis example starts clean
    db_session.delete(admission)
    db_session.commit()


# ---------------------------------------------------------------------------
# 2.4 — Test property-based : échec de réservation empêche la création en base
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 3: Échec de réservation empêche la création en base
@given(data=non_ambulatoire_admission, status_code=error_status_codes)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_reservation_failure_prevents_creation(
    data: CreateAdmission,
    status_code: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 3.1, 3.2, 3.3**

    Pour tout code HTTP != 201 retourné par le Service_Chambres,
    create_admission doit lever une HTTPException et aucune admission
    ne doit être persistée en base de données.
    """
    from fastapi import HTTPException

    # Override patient_id to match the patient actually in DB
    data = data.model_copy(update={"patient_id": patient_in_db.id_patient})

    # Mock the POST to Service_Chambres to return the generated error status_code
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=status_code,
    )

    # Verify that HTTPException is raised
    with pytest.raises(HTTPException):
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    # Verify that no admission was created in the database
    admission_count = db_session.query(Admission).count()
    assert admission_count == 0, (
        f"Expected 0 admissions after reservation failure (status={status_code}), "
        f"but found {admission_count}"
    )


# ---------------------------------------------------------------------------
# 3.1 — Tests unitaires de compensation
# ---------------------------------------------------------------------------


async def test_compensation_on_http_exception_reraises_same(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock, mocker
):
    """Validates: Requirements 4.3

    Quand la réservation réussit mais la création en base échoue avec une
    HTTPException, la compensation (DELETE) est appelée puis la même
    HTTPException est re-levée.
    """
    from fastapi import HTTPException

    data = CreateAdmission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        service_id=1,
    )

    reservation_id = 42
    chambre_id = 7

    # Step 1: POST reservation succeeds (201)
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=201,
        json={"reservation_id": reservation_id, "chambre_id": chambre_id},
    )

    # Step 2: Mock repository create_admission to raise HTTPException
    original_error = HTTPException(status_code=422, detail="db_error")
    mocker.patch.object(
        admission_service.admissions_repository,
        "create_admission",
        side_effect=original_error,
    )

    # Step 3: DELETE compensation succeeds (200)
    httpx_mock.add_response(
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel",
        status_code=200,
        json={"message": "reservation_cancelled"},
    )

    # Assert the same HTTPException is re-raised after compensation
    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "db_error"
    assert exc_info.value is original_error

    # Verify a DELETE call was made for compensation
    delete_requests = [r for r in httpx_mock.get_requests() if r.method == "DELETE"]
    assert len(delete_requests) == 1
    assert f"{reservation_id}/{chambre_id}/cancel" in str(delete_requests[0].url)


async def test_compensation_failure_logs_print(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock, mocker
):
    """Validates: Requirements 5.3

    Quand la compensation échoue (exception lors du DELETE), l'échec est
    journalisé via print et l'erreur originale (pas l'erreur de compensation)
    est propagée au code appelant.
    """
    from fastapi import HTTPException

    data = CreateAdmission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        service_id=1,
    )

    reservation_id = 42
    chambre_id = 7

    # Step 1: POST reservation succeeds (201)
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=201,
        json={"reservation_id": reservation_id, "chambre_id": chambre_id},
    )

    # Step 2: Mock repository create_admission to raise a generic Exception
    mocker.patch.object(
        admission_service.admissions_repository,
        "create_admission",
        side_effect=Exception("db_boom"),
    )

    # Step 3: Make the DELETE compensation call fail with an httpx error
    httpx_mock.add_exception(
        httpx.ConnectError("connection refused"),
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel",
    )

    # Patch builtins.print to verify compensation failure is logged
    mock_print = mocker.patch("builtins.print")

    # Assert the original error is propagated (wrapped as HTTPException 500)
    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    assert exc_info.value.status_code == 500
    assert "db_boom" in exc_info.value.detail

    # Verify print was called to log the compensation failure
    mock_print.assert_called_once()
    print_args = str(mock_print.call_args)
    assert "Compensation failed" in print_args


# ---------------------------------------------------------------------------
# 3.2 — Test property-based : compensation après échec de création en base
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 4: Compensation après échec de création en base
@given(
    data=non_ambulatoire_admission,
    reservation_id=reservation_ids,
    chambre_id=chambre_ids,
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_compensation_on_db_failure(
    data: CreateAdmission,
    reservation_id: int,
    chambre_id: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
    mocker,
):
    """**Validates: Requirements 4.1, 4.2, 4.3**

    Pour toute réservation réussie (statut 201 avec reservation_id et chambre_id)
    suivie d'une exception lors de la création en base, AdmissionService doit
    émettre un appel DELETE vers
    {CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel
    et propager l'erreur originale au code appelant.
    """
    from fastapi import HTTPException

    # Override patient_id to match the patient actually in DB
    data = data.model_copy(update={"patient_id": patient_in_db.id_patient})

    # Step 1: POST reservation succeeds (201)
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=201,
        json={"reservation_id": reservation_id, "chambre_id": chambre_id},
    )

    # Step 2: Mock repository create_admission to raise an Exception (DB failure)
    mocker.patch.object(
        admission_service.admissions_repository,
        "create_admission",
        side_effect=Exception("simulated_db_failure"),
    )

    # Step 3: DELETE compensation succeeds (200)
    httpx_mock.add_response(
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel",
        status_code=200,
        json={"message": "reservation_cancelled"},
    )

    # Record request count before the call to isolate this iteration's requests
    requests_before = len(httpx_mock.get_requests())

    # Act & Assert: the original error is propagated as HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    # Verify the original error is propagated (wrapped as HTTPException 500)
    assert exc_info.value.status_code == 500
    assert "simulated_db_failure" in exc_info.value.detail

    # Verify a DELETE call was made for compensation with correct reservation_id and chambre_id
    new_requests = httpx_mock.get_requests()[requests_before:]
    delete_requests = [r for r in new_requests if r.method == "DELETE"]
    assert len(delete_requests) == 1
    expected_cancel_url = f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel"
    assert str(delete_requests[0].url) == expected_cancel_url


# ---------------------------------------------------------------------------
# 3.3 — Test property-based : résilience de la compensation
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 5: Résilience de la compensation
@given(
    data=non_ambulatoire_admission,
    reservation_id=reservation_ids,
    chambre_id=chambre_ids,
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_compensation_resilience(
    data: CreateAdmission,
    reservation_id: int,
    chambre_id: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
    mocker,
):
    """**Validates: Requirements 5.1, 5.2**

    Pour toute réservation réussie (statut 201) suivie d'une exception lors de
    la création en base, quand la compensation (DELETE) échoue également,
    l'erreur de compensation ne doit PAS se propager. L'erreur propagée au code
    appelant doit être l'erreur originale (celle qui a déclenché la compensation),
    pas l'erreur de compensation.
    """
    from fastapi import HTTPException

    # Override patient_id to match the patient actually in DB
    data = data.model_copy(update={"patient_id": patient_in_db.id_patient})

    # Step 1: POST reservation succeeds (201)
    httpx_mock.add_response(
        method="POST",
        url=f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
        status_code=201,
        json={"reservation_id": reservation_id, "chambre_id": chambre_id},
    )

    # Step 2: Mock repository create_admission to raise an Exception (original error)
    original_error_message = f"original_db_error_{reservation_id}"
    mocker.patch.object(
        admission_service.admissions_repository,
        "create_admission",
        side_effect=Exception(original_error_message),
    )

    # Step 3: Make the DELETE compensation call FAIL (compensation error)
    httpx_mock.add_exception(
        httpx.ConnectError("compensation_network_failure"),
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel",
    )

    # Act & Assert: the original error is propagated, NOT the compensation error
    with pytest.raises(HTTPException) as exc_info:
        await admission_service.create_admission(
            db=db_session,
            data=data,
            internal_payload="fake-token",
            request=mock_request,
        )

    # 1. The compensation error does NOT propagate (we got HTTPException, not ConnectError)
    assert isinstance(exc_info.value, HTTPException)

    # 2. The original error IS propagated to the caller
    assert exc_info.value.status_code == 500

    # 3. The propagated error contains the original error message, NOT the compensation error
    assert original_error_message in exc_info.value.detail
    assert "compensation_network_failure" not in exc_info.value.detail


# ---------------------------------------------------------------------------
# 5.1 — Tests unitaires de suppression
# ---------------------------------------------------------------------------


async def test_delete_returns_admission_deleted_message(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock
):
    """Validates: Requirements 6.3

    Quand une admission non ambulatoire avec ref_reservation est supprimée
    et que l'annulation de réservation réussit (200), delete_admission
    retourne {"message": "admission_deleted"}.
    """
    # Create a non-ambulatoire admission in the DB with ref_reservation set
    admission = Admission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        ref_reservation=42,
    )
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)

    # Mock the DELETE to Service_Chambres to return 200
    httpx_mock.add_response(
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{admission.ref_reservation}/cancel",
        status_code=200,
        json={"message": "reservation_cancelled"},
    )

    result = await admission_service.delete_admission(
        db=db_session,
        admission_id=admission.id_admission,
        internal_payload="fake-token",
        request=mock_request,
    )

    assert result == {"message": "admission_deleted"}


async def test_delete_ambulatoire_returns_admission_deleted(
    admission_service, mock_request, patient_in_db, db_session, httpx_mock
):
    """Validates: Requirements 7.2

    Quand une admission ambulatoire est supprimée, delete_admission retourne
    {"message": "admission_deleted"} sans effectuer d'appel HTTP.
    """
    # Create an ambulatoire admission in the DB (ref_reservation=None)
    admission = Admission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=True,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        ref_reservation=None,
    )
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)

    result = await admission_service.delete_admission(
        db=db_session,
        admission_id=admission.id_admission,
        internal_payload="fake-token",
        request=mock_request,
    )

    assert result == {"message": "admission_deleted"}
    # Verify no HTTP calls were made
    assert httpx_mock.get_requests() == []


async def test_delete_nonexistent_admission_raises_404(
    admission_service, mock_request, db_session
):
    """Validates: Requirements 9.1

    Quand une suppression est demandée pour un admission_id inexistant,
    delete_admission lève HTTPException(404, 'admission_not_found').
    """
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await admission_service.delete_admission(
            db=db_session,
            admission_id=99999,
            internal_payload="fake-token",
            request=MagicMock(headers={"X-Real-IP": "127.0.0.1", "X-Forwarded-For": "127.0.0.1"}),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "admission_not_found"


# ---------------------------------------------------------------------------
# 5.2 — Test property-based : suppression avec annulation de réservation
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 6: Suppression avec annulation de réservation
@given(reservation_id=reservation_ids)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_delete_with_reservation_cancellation(
    reservation_id: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 6.1, 6.2, 6.3**

    Pour toute admission non ambulatoire avec ref_reservation non nul,
    delete_admission doit émettre un appel DELETE vers le Service_Chambres,
    l'admission doit être supprimée de la base de données, et le résultat
    doit être {"message": "admission_deleted"}.
    """
    # 1. Create a non-ambulatoire Admission directly in the DB with ref_reservation
    admission = Admission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        ref_reservation=reservation_id,
    )
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)
    admission_id = admission.id_admission

    # 2. Mock the DELETE to Service_Chambres to return 200
    #    The service uses: {CHAMBRES_SERVICE}/chambres/{ref_reservation}/cancel
    httpx_mock.add_response(
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/cancel",
        status_code=200,
        json={"message": "reservation_cancelled"},
    )

    # Record requests before the call to isolate this iteration's requests
    requests_before = len(httpx_mock.get_requests())

    # 3. Call delete_admission
    result = await admission_service.delete_admission(
        db=db_session,
        admission_id=admission_id,
        internal_payload="fake-token",
        request=mock_request,
    )

    # 4. Verify a DELETE call was made to the Service_Chambres
    new_requests = httpx_mock.get_requests()[requests_before:]
    delete_requests = [r for r in new_requests if r.method == "DELETE"]
    assert len(delete_requests) == 1
    expected_url = f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/cancel"
    assert str(delete_requests[0].url) == expected_url

    # 5. Verify the admission is deleted from the DB (query by id returns None)
    deleted = db_session.query(Admission).filter(
        Admission.id_admission == admission_id
    ).first()
    assert deleted is None

    # 6. Verify the result is {"message": "admission_deleted"}
    assert result == {"message": "admission_deleted"}


# ---------------------------------------------------------------------------
# 5.3 — Test property-based : suppression ambulatoire sans appel HTTP
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 7: Suppression ambulatoire sans appel HTTP
@given(data=ambulatoire_admission)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_delete_ambulatoire_no_http(
    data: CreateAdmission,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 7.1, 7.2**

    Pour toute admission ambulatoire, delete_admission doit supprimer
    l'admission de la base de données sans émettre d'appel HTTP vers
    le Service_Chambres, et retourner {"message": "admission_deleted"}.
    """
    # 1. Create an ambulatoire Admission directly in the DB with ref_reservation=None
    admission = Admission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=True,
        entree_le=data.entree_le,
        sortie_prevue_le=data.sortie_prevue_le,
        ref_reservation=None,
    )
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)
    admission_id = admission.id_admission

    # 2. Call delete_admission with the admission's ID
    result = await admission_service.delete_admission(
        db=db_session,
        admission_id=admission_id,
        internal_payload="fake-token",
        request=mock_request,
    )

    # 3. Verify the result is {"message": "admission_deleted"}
    assert result == {"message": "admission_deleted"}

    # 4. Verify no HTTP calls were made
    assert httpx_mock.get_requests() == []

    # 5. Verify the admission is deleted from the DB
    deleted = db_session.query(Admission).filter(
        Admission.id_admission == admission_id
    ).first()
    assert deleted is None


# ---------------------------------------------------------------------------
# 5.4 — Test property-based : échec d'annulation préserve l'admission
# ---------------------------------------------------------------------------


# Feature: saga-pattern-tests, Property 8: Échec d'annulation préserve l'admission
@given(reservation_id=reservation_ids, status_code=cancel_failure_codes)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_prop_cancel_failure_preserves_admission(
    reservation_id: int,
    status_code: int,
    admission_service,
    mock_request,
    patient_in_db,
    db_session,
    httpx_mock,
):
    """**Validates: Requirements 8.1, 8.2, 8.3**

    Pour tout code de statut HTTP != 200 et != 404 retourné par le
    Service_Chambres lors de l'annulation d'une réservation,
    delete_admission doit lever une HTTPException avec le statut 400
    et le détail 'failed_to_cancel_reservation', et l'admission doit
    toujours être présente en base de données.
    """
    from fastapi import HTTPException

    # 1. Create a non-ambulatoire Admission directly in the DB with ref_reservation
    admission = Admission(
        patient_id=patient_in_db.id_patient,
        ambulatoire=False,
        entree_le=datetime(2025, 6, 1),
        sortie_prevue_le=datetime(2025, 6, 5),
        ref_reservation=reservation_id,
    )
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)
    admission_id = admission.id_admission

    # 2. Mock the DELETE to Service_Chambres to return the generated error status_code
    httpx_mock.add_response(
        method="DELETE",
        url=f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/cancel",
        status_code=status_code,
    )

    # 3. Call delete_admission and verify HTTPException 400 is raised
    with pytest.raises(HTTPException) as exc_info:
        await admission_service.delete_admission(
            db=db_session,
            admission_id=admission_id,
            internal_payload="fake-token",
            request=mock_request,
        )

    # 4. Verify HTTPException 400 with detail 'failed_to_cancel_reservation'
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "failed_to_cancel_reservation"

    # 5. Verify the admission is still in the DB (not deleted)
    preserved = db_session.query(Admission).filter(
        Admission.id_admission == admission_id
    ).first()
    assert preserved is not None, (
        f"Admission {admission_id} should still exist after cancel failure "
        f"(status_code={status_code})"
    )

    # Cleanup: remove the admission so next Hypothesis example starts clean
    db_session.delete(preserved)
    db_session.commit()
