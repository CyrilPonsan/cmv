"""Tests property-based pour le SagaEngine — saga-resilience-improvement.

Valide les propriétés de correction du SagaEngine via Hypothesis :
logging structuré, ordre des opérations, rollback, outbox, transactions,
et transmission des headers d'authentification.
"""

import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.outbox_crud import PgOutboxRepository
from app.services.saga_engine import SagaEngine
from app.sql.models import Admission, Base, OutboxEntry, OutboxStatus


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

admission_ids = st.integers(min_value=1, max_value=100_000)
reservation_ids = st.integers(min_value=1, max_value=100_000)
patient_ids = st.integers(min_value=1, max_value=100_000)
error_messages = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=1,
    max_size=120,
)
error_status_codes = st.integers(min_value=100, max_value=599).filter(
    lambda x: x not in (200, 404)
)
success_status_codes = st.sampled_from([200, 404])
tokens = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=8,
    max_size=64,
).map(lambda t: f"Bearer {t}")
ip_addresses = st.tuples(
    st.integers(min_value=1, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=1, max_value=254),
).map(lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}")


# ---------------------------------------------------------------------------
# Per-iteration DB session helper
# ---------------------------------------------------------------------------

# We use a module-level engine so Hypothesis iterations each get a fresh
# session via _fresh_session(), avoiding stale-state issues after rollback.

_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_ENGINE)
_SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


def _fresh_session():
    """Return a new session after cleaning all rows."""
    session = _SessionFactory()
    session.query(OutboxEntry).delete()
    session.query(Admission).delete()
    session.commit()
    return session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DEFAULT_HEADERS = {
    "Authorization": "Bearer x",
    "X-Real-IP": "1.2.3.4",
    "X-Forwarded-For": "1.2.3.4",
}


def _make_admission(admission_id, patient_id, ref_reservation):
    return Admission(
        id_admission=admission_id,
        patient_id=patient_id,
        ambulatoire=False,
        ref_reservation=ref_reservation,
        entree_le=datetime(2026, 1, 1),
        sortie_prevue_le=datetime(2026, 1, 5),
    )


def _insert_admission(session, admission_id, patient_id, ref_reservation):
    adm = _make_admission(admission_id, patient_id, ref_reservation)
    session.add(adm)
    session.commit()
    session.refresh(adm)
    return adm


def _build_engine(logger=None, http_client=None, outbox_repo=None):
    return SagaEngine(
        admissions_repository=PgAdmissionsRepository(),
        outbox_repository=outbox_repo or PgOutboxRepository(),
        logger=logger or MagicMock(spec=logging.Logger),
        http_client=http_client or AsyncMock(spec=httpx.AsyncClient),
    )


# ---------------------------------------------------------------------------
# 2.2 — Property 1 : Logging structuré des compensations
# Feature: saga-resilience-improvement, Property 1: Logging structuré des compensations
# ---------------------------------------------------------------------------


class TestProperty1LoggingStructure:
    """**Validates: Requirements 1.1, 1.2**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=success_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_success_logs_info_with_admission_and_type(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Pour toute compensation réussie (200/404), logger.info est appelé
        avec admission_id et compensation_type."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            info_calls = [str(c) for c in logger.info.call_args_list]
            assert any(
                str(admission_id) in c and str(reservation_id) in c
                for c in info_calls
            ), f"Expected logger.info with admission_id={admission_id}, got: {info_calls}"
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_failure_logs_error_with_details(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Pour toute compensation échouée (code != 200/404), logger.error est
        appelé avec admission_id, reservation_id, et le message d'erreur."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            error_calls = [str(c) for c in logger.error.call_args_list]
            assert any(
                str(reservation_id) in c and str(admission_id) in c
                for c in error_calls
            ), f"Expected logger.error with ids, got: {error_calls}"
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        error_msg=error_messages,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_network_error_logs_error_with_details(
        self,
        admission_id,
        reservation_id,
        patient_id,
        error_msg,
    ):
        """Pour toute erreur réseau, logger.error est appelé avec les détails."""
        session = _fresh_session()
        try:
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.side_effect = httpx.ConnectError(error_msg)
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            error_calls = [str(c) for c in logger.error.call_args_list]
            assert any(
                str(reservation_id) in c and str(admission_id) in c
                for c in error_calls
            ), f"Expected logger.error with ids"
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.3 — Property 2 : Annulation de réservation avant suppression
# Feature: saga-resilience-improvement, Property 2: Annulation de réservation avant suppression
# ---------------------------------------------------------------------------


class TestProperty2CancelBeforeDelete:
    """**Validates: Requirements 2.3**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_http_delete_called_before_admission_deleted(
        self,
        admission_id,
        reservation_id,
        patient_id,
    ):
        """Pour toute admission non-ambulatoire avec ref_reservation,
        l'appel HTTP DELETE doit précéder la suppression de l'admission en DB."""
        session = _fresh_session()
        try:
            call_order = []

            mock_response = MagicMock()
            mock_response.status_code = 200
            http_client = AsyncMock(spec=httpx.AsyncClient)

            async def track_delete(*args, **kwargs):
                call_order.append("http_delete")
                return mock_response

            http_client.delete.side_effect = track_delete

            original_query = session.query

            def tracked_query(*args, **kwargs):
                result = original_query(*args, **kwargs)
                if args and args[0] is Admission:
                    original_filter = result.filter

                    def tracked_filter(*fargs, **fkwargs):
                        filtered = original_filter(*fargs, **fkwargs)
                        original_del = filtered.delete

                        def tracked_del(*dargs, **dkwargs):
                            call_order.append("db_delete")
                            return original_del(*dargs, **dkwargs)

                        filtered.delete = tracked_del
                        return filtered

                    result.filter = tracked_filter
                return result

            session.query = tracked_query

            logger = MagicMock(spec=logging.Logger)
            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            session.query = original_query

            assert "http_delete" in call_order, "HTTP DELETE was never called"
            assert "db_delete" in call_order, "DB DELETE was never called"
            assert call_order.index("http_delete") < call_order.index("db_delete"), (
                f"HTTP DELETE must happen BEFORE DB DELETE, order was: {call_order}"
            )
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.4 — Property 3 : Rollback sur échec d'annulation
# Feature: saga-resilience-improvement, Property 3: Rollback sur échec d'annulation
# ---------------------------------------------------------------------------


class TestProperty3RollbackOnCancelFailure:
    """**Validates: Requirements 2.4**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_rollback_on_http_error_admission_persists(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Pour tout code HTTP != 200/404, le SagaEngine doit rollback
        et l'admission doit rester en base."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception) as exc_info:
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            assert exc_info.value.status_code == 400

            remaining = (
                session.query(Admission)
                .filter(Admission.id_admission == admission_id)
                .first()
            )
            assert remaining is not None, (
                f"Admission {admission_id} should persist after rollback (HTTP {status_code})"
            )
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_rollback_on_network_error_admission_persists(
        self,
        admission_id,
        reservation_id,
        patient_id,
    ):
        """Pour toute erreur réseau, le SagaEngine doit rollback
        et l'admission doit rester en base."""
        session = _fresh_session()
        try:
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.side_effect = httpx.ConnectError("network failure")
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception) as exc_info:
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            assert exc_info.value.status_code == 400

            remaining = (
                session.query(Admission)
                .filter(Admission.id_admission == admission_id)
                .first()
            )
            assert remaining is not None, (
                f"Admission {admission_id} should persist after network error rollback"
            )
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.5 — Property 4 : Insertion outbox sur échec de compensation
# Feature: saga-resilience-improvement, Property 4: Insertion outbox sur échec de compensation
# ---------------------------------------------------------------------------


class TestProperty4OutboxInsertionOnFailure:
    """**Validates: Requirements 3.2, 3.6**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_outbox_entry_has_correct_payload_on_http_error(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Pour tout échec HTTP, l'entrée outbox doit contenir le bon payload
        avec status PENDING et retry_count=0."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            outbox_repo = AsyncMock(spec=PgOutboxRepository)
            engine = _build_engine(
                logger=logger, http_client=http_client, outbox_repo=outbox_repo
            )
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            outbox_repo.create_entry.assert_called_once()
            entry_arg = outbox_repo.create_entry.call_args[0][1]

            assert entry_arg.compensation_type == "cancel_reservation"
            assert entry_arg.retry_count == 0
            assert entry_arg.payload["reservation_id"] == reservation_id
            assert entry_arg.payload["admission_id"] == admission_id
            assert "endpoint" in entry_arg.payload
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        error_msg=error_messages,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_outbox_entry_has_correct_payload_on_network_error(
        self,
        admission_id,
        reservation_id,
        patient_id,
        error_msg,
    ):
        """Pour toute erreur réseau, l'entrée outbox doit contenir le bon payload."""
        session = _fresh_session()
        try:
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.side_effect = httpx.ConnectError(error_msg)
            logger = MagicMock(spec=logging.Logger)

            outbox_repo = AsyncMock(spec=PgOutboxRepository)
            engine = _build_engine(
                logger=logger, http_client=http_client, outbox_repo=outbox_repo
            )
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            outbox_repo.create_entry.assert_called_once()
            entry_arg = outbox_repo.create_entry.call_args[0][1]

            assert entry_arg.compensation_type == "cancel_reservation"
            assert entry_arg.retry_count == 0
            assert entry_arg.payload["reservation_id"] == reservation_id
            assert entry_arg.payload["admission_id"] == admission_id
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.6 — Property 7 : Transaction atomique du saga
# Feature: saga-resilience-improvement, Property 7: Transaction atomique du saga
# ---------------------------------------------------------------------------


class TestProperty7AtomicTransaction:
    """**Validates: Requirements 4.1, 4.3**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=success_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_commit_called_exactly_once_after_all_steps(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """db.commit() doit être appelé exactement une fois, après toutes
        les étapes locales."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            commit_count = 0
            original_commit = session.commit

            def counting_commit():
                nonlocal commit_count
                commit_count += 1
                original_commit()

            session.commit = counting_commit

            await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            session.commit = original_commit

            assert commit_count == 1, (
                f"Expected exactly 1 commit, got {commit_count}"
            )
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_no_commit_on_compensation_failure(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Quand la compensation échoue, db.commit() ne doit PAS être appelé."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            commit_count = 0
            original_commit = session.commit

            def counting_commit():
                nonlocal commit_count
                commit_count += 1
                original_commit()

            session.commit = counting_commit

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            session.commit = original_commit

            assert commit_count == 0, (
                f"Expected 0 commits on failure, got {commit_count}"
            )
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.7 — Property 8 : Rollback complet sur exception
# Feature: saga-resilience-improvement, Property 8: Rollback complet sur exception
# ---------------------------------------------------------------------------


class TestProperty8FullRollbackOnException:
    """**Validates: Requirements 4.2**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_rollback_called_on_exception_during_delete(
        self,
        admission_id,
        reservation_id,
        patient_id,
    ):
        """Sur toute exception pendant les étapes locales du saga,
        db.rollback() doit être appelé et aucune modification ne persiste."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = 200
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            rollback_count = 0
            original_rollback = session.rollback
            original_flush = session.flush

            def counting_rollback():
                nonlocal rollback_count
                rollback_count += 1
                original_rollback()

            def failing_flush():
                raise RuntimeError("simulated flush failure")

            session.rollback = counting_rollback
            session.flush = failing_flush

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            session.rollback = original_rollback
            session.flush = original_flush

            assert rollback_count >= 1, "db.rollback() must be called on exception"

            remaining = (
                session.query(Admission)
                .filter(Admission.id_admission == admission_id)
                .first()
            )
            assert remaining is not None, (
                f"Admission {admission_id} must persist after rollback on exception"
            )
        finally:
            session.rollback()
            session.close()

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_rollback_on_cancel_failure_no_modifications_persist(
        self,
        admission_id,
        reservation_id,
        patient_id,
        status_code,
    ):
        """Sur échec d'annulation, rollback est appelé et l'admission persiste."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            rollback_count = 0
            original_rollback = session.rollback

            def counting_rollback():
                nonlocal rollback_count
                rollback_count += 1
                original_rollback()

            session.rollback = counting_rollback

            with pytest.raises(Exception):
                await engine.execute_delete_admission(session, adm, _DEFAULT_HEADERS)

            session.rollback = original_rollback

            assert rollback_count >= 1, "db.rollback() must be called on cancel failure"

            remaining = (
                session.query(Admission)
                .filter(Admission.id_admission == admission_id)
                .first()
            )
            assert remaining is not None
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 2.8 — Property 9 : Transmission des headers d'authentification
# Feature: saga-resilience-improvement, Property 9: Transmission des headers d'authentification
# ---------------------------------------------------------------------------


class TestProperty9AuthHeaders:
    """**Validates: Requirements 5.1**"""

    @given(
        admission_id=admission_ids,
        reservation_id=reservation_ids,
        patient_id=patient_ids,
        token=tokens,
        real_ip=ip_addresses,
        forwarded_for=ip_addresses,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_headers_forwarded_to_http_request(
        self,
        admission_id,
        reservation_id,
        patient_id,
        token,
        real_ip,
        forwarded_for,
    ):
        """Pour toute compensation HTTP, la requête doit inclure
        Authorization, X-Real-IP et X-Forwarded-For avec les valeurs
        transmises par l'appelant."""
        session = _fresh_session()
        try:
            mock_response = MagicMock()
            mock_response.status_code = 200
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)
            adm = _insert_admission(session, admission_id, patient_id, reservation_id)

            headers = {
                "Authorization": token,
                "X-Real-IP": real_ip,
                "X-Forwarded-For": forwarded_for,
            }

            await engine.execute_delete_admission(session, adm, headers)

            http_client.delete.assert_called_once()
            call_kwargs = http_client.delete.call_args
            sent_headers = call_kwargs.kwargs.get("headers", {})

            assert sent_headers["Authorization"] == token, (
                f"Expected Authorization={token}, got {sent_headers.get('Authorization')}"
            )
            assert sent_headers["X-Real-IP"] == real_ip, (
                f"Expected X-Real-IP={real_ip}, got {sent_headers.get('X-Real-IP')}"
            )
            assert sent_headers["X-Forwarded-For"] == forwarded_for, (
                f"Expected X-Forwarded-For={forwarded_for}, got {sent_headers.get('X-Forwarded-For')}"
            )
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 4.2 — Property 5 : Cycle de vie du retry outbox
# Feature: saga-resilience-improvement, Property 5: Cycle de vie du retry outbox
# ---------------------------------------------------------------------------


retry_counts = st.integers(min_value=0, max_value=10)
max_retries_values = st.integers(min_value=1, max_value=10)


def _insert_outbox_entry(session, entry_id, retry_count, reservation_id, admission_id):
    """Insert an outbox entry with PENDING status for retry testing."""
    entry = OutboxEntry(
        id=entry_id,
        compensation_type="cancel_reservation",
        payload={
            "reservation_id": reservation_id,
            "admission_id": admission_id,
            "chambres_service_url": "http://localhost:8003/api",
            "endpoint": f"/chambres/{reservation_id}/cancel",
        },
        retry_count=retry_count,
        status=OutboxStatus.PENDING,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


class TestProperty5RetryLifecycle:
    """**Validates: Requirements 3.3, 3.4, 3.6**"""

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        retry_count=retry_counts,
        max_retries=max_retries_values,
        status_code=success_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_successful_retry_marks_completed(
        self,
        reservation_id,
        admission_id,
        retry_count,
        max_retries,
        status_code,
    ):
        """Pour toute entrée outbox pending avec retry_count < max_retries,
        si la compensation réussit (200/404), le statut doit passer à COMPLETED."""
        # Only test entries that would be picked up by get_pending_entries
        from hypothesis import assume

        assume(retry_count < max_retries)

        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, retry_count, reservation_id, admission_id
            )

            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            result = await engine.retry_pending_compensations(session, max_retries)

            session.refresh(entry)
            assert entry.status == OutboxStatus.COMPLETED, (
                f"Expected COMPLETED after successful retry, got {entry.status}"
            )
            assert result["successes"] >= 1
        finally:
            session.rollback()
            session.close()

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        retry_count=retry_counts,
        max_retries=max_retries_values,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_failed_retry_increments_count_and_stays_pending(
        self,
        reservation_id,
        admission_id,
        retry_count,
        max_retries,
        status_code,
    ):
        """Pour toute entrée outbox pending avec retry_count < max_retries,
        si la compensation échoue, retry_count doit être incrémenté et le
        statut doit rester PENDING (si le seuil n'est pas atteint)."""
        from hypothesis import assume

        assume(retry_count < max_retries)
        # After increment, retry_count+1 must still be < max_retries to stay PENDING
        assume(retry_count + 1 < max_retries)

        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, retry_count, reservation_id, admission_id
            )
            original_retry_count = entry.retry_count

            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            result = await engine.retry_pending_compensations(session, max_retries)

            session.refresh(entry)
            assert entry.retry_count == original_retry_count + 1, (
                f"Expected retry_count={original_retry_count + 1}, "
                f"got {entry.retry_count}"
            )
            assert entry.status == OutboxStatus.PENDING, (
                f"Expected PENDING after failed retry below threshold, "
                f"got {entry.status}"
            )
            assert result["failures"] >= 1
        finally:
            session.rollback()
            session.close()

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        retry_count=retry_counts,
        max_retries=max_retries_values,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_network_error_retry_increments_count(
        self,
        reservation_id,
        admission_id,
        retry_count,
        max_retries,
    ):
        """Pour toute erreur réseau lors du retry, retry_count doit être
        incrémenté et le statut doit rester PENDING (si seuil non atteint)."""
        from hypothesis import assume

        assume(retry_count < max_retries)
        assume(retry_count + 1 < max_retries)

        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, retry_count, reservation_id, admission_id
            )
            original_retry_count = entry.retry_count

            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.side_effect = httpx.ConnectError("network failure")
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            await engine.retry_pending_compensations(session, max_retries)

            session.refresh(entry)
            assert entry.retry_count == original_retry_count + 1
            assert entry.status == OutboxStatus.PENDING
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 4.3 — Property 6 : Seuil de retry atteint
# Feature: saga-resilience-improvement, Property 6: Seuil de retry atteint
# ---------------------------------------------------------------------------


class TestProperty6RetryThresholdReached:
    """**Validates: Requirements 3.5**"""

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        max_retries=st.integers(min_value=1, max_value=10),
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_threshold_reached_marks_failed_and_logs_critical(
        self,
        reservation_id,
        admission_id,
        max_retries,
        status_code,
    ):
        """Pour toute entrée outbox dont retry_count atteint max_retries
        après un échec, le statut doit passer à FAILED et logger.critical
        doit être appelé."""
        session = _fresh_session()
        try:
            # Set retry_count to max_retries - 1 so that after increment
            # it reaches max_retries and triggers the threshold
            entry = _insert_outbox_entry(
                session, 1, max_retries - 1, reservation_id, admission_id
            )

            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            await engine.retry_pending_compensations(session, max_retries)

            session.refresh(entry)
            assert entry.status == OutboxStatus.FAILED, (
                f"Expected FAILED when retry threshold reached, got {entry.status}"
            )
            assert logger.critical.called, (
                "logger.critical must be called when retry threshold is reached"
            )
        finally:
            session.rollback()
            session.close()

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        max_retries=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_threshold_reached_on_network_error_marks_failed(
        self,
        reservation_id,
        admission_id,
        max_retries,
    ):
        """Pour toute erreur réseau quand retry_count atteint le seuil,
        le statut doit passer à FAILED et logger.critical doit être appelé."""
        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, max_retries - 1, reservation_id, admission_id
            )

            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.side_effect = httpx.ConnectError("network failure")
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            await engine.retry_pending_compensations(session, max_retries)

            session.refresh(entry)
            assert entry.status == OutboxStatus.FAILED, (
                f"Expected FAILED on network error at threshold, got {entry.status}"
            )
            assert logger.critical.called, (
                "logger.critical must be called on network error at threshold"
            )
            # Verify critical log includes entry id and retry info
            critical_calls = [str(c) for c in logger.critical.call_args_list]
            assert any(
                str(entry.id) in c for c in critical_calls
            ), f"logger.critical should include entry id, got: {critical_calls}"
        finally:
            session.rollback()
            session.close()


# ---------------------------------------------------------------------------
# 4.4 — Property 10 : Token de service pour les retries outbox
# Feature: saga-resilience-improvement, Property 10: Token de service pour les retries outbox
# ---------------------------------------------------------------------------


class TestProperty10ServiceTokenForRetries:
    """**Validates: Requirements 5.2**"""

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        retry_count=retry_counts,
        max_retries=max_retries_values,
        status_code=success_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_retry_uses_service_token_not_user_token(
        self,
        reservation_id,
        admission_id,
        retry_count,
        max_retries,
        status_code,
    ):
        """Pour toute compensation rejouée depuis l'outbox, la requête HTTP
        doit utiliser un token de service (Bearer ...) et non le token
        utilisateur original du payload."""
        from hypothesis import assume

        assume(retry_count < max_retries)

        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, retry_count, reservation_id, admission_id
            )

            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            await engine.retry_pending_compensations(session, max_retries)

            http_client.delete.assert_called_once()
            call_kwargs = http_client.delete.call_args
            sent_headers = call_kwargs.kwargs.get(
                "headers", call_kwargs[1].get("headers", {}) if len(call_kwargs) > 1 else {}
            )

            auth_header = sent_headers.get("Authorization", "")
            assert auth_header.startswith("Bearer "), (
                f"Authorization header must start with 'Bearer ', got: '{auth_header}'"
            )
            # The token part must not be empty
            token_value = auth_header[len("Bearer "):]
            assert len(token_value) > 0, (
                "Service token must not be empty after 'Bearer ' prefix"
            )
        finally:
            session.rollback()
            session.close()

    @given(
        reservation_id=reservation_ids,
        admission_id=admission_ids,
        retry_count=retry_counts,
        max_retries=max_retries_values,
        status_code=error_status_codes,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_retry_service_token_on_failure_path(
        self,
        reservation_id,
        admission_id,
        retry_count,
        max_retries,
        status_code,
    ):
        """Même sur le chemin d'échec, le retry doit utiliser un token de
        service et non le token utilisateur original."""
        from hypothesis import assume

        assume(retry_count < max_retries)

        session = _fresh_session()
        try:
            entry = _insert_outbox_entry(
                session, 1, retry_count, reservation_id, admission_id
            )

            mock_response = MagicMock()
            mock_response.status_code = status_code
            http_client = AsyncMock(spec=httpx.AsyncClient)
            http_client.delete.return_value = mock_response
            logger = MagicMock(spec=logging.Logger)

            engine = _build_engine(logger=logger, http_client=http_client)

            await engine.retry_pending_compensations(session, max_retries)

            http_client.delete.assert_called_once()
            call_kwargs = http_client.delete.call_args
            sent_headers = call_kwargs.kwargs.get(
                "headers", call_kwargs[1].get("headers", {}) if len(call_kwargs) > 1 else {}
            )

            auth_header = sent_headers.get("Authorization", "")
            assert auth_header.startswith("Bearer "), (
                f"Authorization header must start with 'Bearer ', got: '{auth_header}'"
            )
            token_value = auth_header[len("Bearer "):]
            assert len(token_value) > 0, (
                "Service token must not be empty after 'Bearer ' prefix"
            )
        finally:
            session.rollback()
            session.close()
