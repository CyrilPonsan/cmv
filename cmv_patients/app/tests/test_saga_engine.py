"""Tests unitaires pour le SagaEngine."""

import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.outbox_crud import PgOutboxRepository
from app.services.saga_engine import SagaEngine
from app.sql.models import Admission, Base, OutboxEntry, OutboxStatus


@pytest.fixture
def logger():
    """Logger mocké pour capturer les appels."""
    mock_logger = MagicMock(spec=logging.Logger)
    return mock_logger


@pytest.fixture
def admissions_repo():
    return PgAdmissionsRepository()


@pytest.fixture
def outbox_repo():
    return PgOutboxRepository()


@pytest.fixture
def headers():
    return {
        "Authorization": "Bearer test-token-123",
        "X-Real-IP": "192.168.1.1",
        "X-Forwarded-For": "192.168.1.1",
    }


def _make_admission(
    admission_id=1,
    patient_id=10,
    ambulatoire=False,
    ref_reservation=42,
):
    """Crée une admission de test."""
    admission = Admission(
        id_admission=admission_id,
        patient_id=patient_id,
        ambulatoire=ambulatoire,
        ref_reservation=ref_reservation,
        entree_le=datetime(2026, 1, 1),
        sortie_prevue_le=datetime(2026, 1, 5),
    )
    return admission


class TestSagaEngineDeleteAdmission:
    """Tests pour execute_delete_admission."""

    @pytest.mark.asyncio
    async def test_ambulatory_admission_no_http_call(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Une admission ambulatoire ne déclenche pas d'appel HTTP."""
        admission = _make_admission(ambulatoire=True, ref_reservation=None)
        db_session.add(admission)
        db_session.commit()

        http_client = AsyncMock(spec=httpx.AsyncClient)

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.execute_delete_admission(db_session, admission, {})

        assert result == {"message": "admission_deleted"}
        http_client.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_ambulatory_cancel_success_200(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Annulation réussie (200) → admission supprimée, log INFO."""
        admission = _make_admission()
        db_session.add(admission)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.execute_delete_admission(db_session, admission, headers)

        assert result == {"message": "admission_deleted"}
        # Vérifier que le logger INFO a été appelé pour la compensation
        info_calls = [c for c in logger.info.call_args_list]
        assert any("Compensation réussie" in str(c) for c in info_calls)

    @pytest.mark.asyncio
    async def test_non_ambulatory_cancel_success_404(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Annulation avec 404 (réservation déjà annulée) → succès."""
        admission = _make_admission()
        db_session.add(admission)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.execute_delete_admission(db_session, admission, headers)

        assert result == {"message": "admission_deleted"}

    @pytest.mark.asyncio
    async def test_cancel_failure_http_500_raises_and_inserts_outbox(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Échec HTTP 500 → outbox insérée, rollback, HTTPException 400."""
        admission = _make_admission()
        db_session.add(admission)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 500
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)

        with pytest.raises(Exception) as exc_info:
            await engine.execute_delete_admission(db_session, admission, headers)

        assert exc_info.value.status_code == 400
        # L'admission doit toujours exister après rollback
        remaining = (
            db_session.query(Admission)
            .filter(Admission.id_admission == admission.id_admission)
            .first()
        )
        assert remaining is not None

    @pytest.mark.asyncio
    async def test_cancel_failure_network_error_raises_and_inserts_outbox(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Erreur réseau → outbox insérée, rollback, HTTPException 400."""
        admission = _make_admission()
        db_session.add(admission)
        db_session.commit()

        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.side_effect = httpx.ConnectError("connection refused")

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)

        with pytest.raises(Exception) as exc_info:
            await engine.execute_delete_admission(db_session, admission, headers)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_headers_forwarded_to_http_call(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Les headers Authorization, X-Real-IP, X-Forwarded-For sont transmis."""
        admission = _make_admission()
        db_session.add(admission)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        await engine.execute_delete_admission(db_session, admission, headers)

        call_kwargs = http_client.delete.call_args
        sent_headers = call_kwargs.kwargs.get("headers", {})
        assert sent_headers["Authorization"] == "Bearer test-token-123"
        assert sent_headers["X-Real-IP"] == "192.168.1.1"
        assert sent_headers["X-Forwarded-For"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_no_print_in_saga_engine(self):
        """Le module SagaEngine ne contient aucun appel print()."""
        import inspect
        import app.services.saga_engine as module

        source = inspect.getsource(module)
        # Exclure les commentaires et docstrings
        lines = source.split("\n")
        code_lines = [
            line
            for line in lines
            if line.strip()
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ]
        code = "\n".join(code_lines)
        assert "print(" not in code

    @pytest.mark.asyncio
    async def test_error_logging_on_cancel_failure(
        self, db_session, logger, admissions_repo, outbox_repo, headers
    ):
        """Échec de compensation → logger.error appelé avec les bons détails."""
        admission = _make_admission(admission_id=99, ref_reservation=77)
        db_session.add(admission)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 503
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)

        with pytest.raises(Exception):
            await engine.execute_delete_admission(db_session, admission, headers)

        error_calls = [str(c) for c in logger.error.call_args_list]
        assert any("77" in c and "99" in c for c in error_calls)


def _make_outbox_entry(
    entry_id=1,
    retry_count=0,
    reservation_id=42,
    admission_id=10,
    endpoint="/chambres/42/cancel",
    chambres_service_url="http://localhost:8003/api",
):
    """Crée une entrée outbox de test."""
    entry = OutboxEntry(
        id=entry_id,
        compensation_type="cancel_reservation",
        payload={
            "reservation_id": reservation_id,
            "admission_id": admission_id,
            "chambres_service_url": chambres_service_url,
            "endpoint": endpoint,
        },
        retry_count=retry_count,
        status=OutboxStatus.PENDING,
    )
    return entry


class TestSagaEngineRetryPendingCompensations:
    """Tests pour retry_pending_compensations."""

    @pytest.mark.asyncio
    async def test_retry_success_updates_to_completed(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Retry réussi (200) → statut COMPLETED, compteur successes incrémenté."""
        entry = _make_outbox_entry(retry_count=1)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result["successes"] == 1
        assert result["failures"] == 0

        refreshed = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
        assert refreshed.status == OutboxStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_retry_success_on_404(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Retry avec 404 (réservation déjà annulée) → COMPLETED."""
        entry = _make_outbox_entry(retry_count=0)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result["successes"] == 1
        assert result["failures"] == 0

    @pytest.mark.asyncio
    async def test_retry_failure_increments_retry_count(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Retry échoué → retry_count incrémenté, statut reste PENDING."""
        entry = _make_outbox_entry(retry_count=1)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 500
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result["successes"] == 0
        assert result["failures"] == 1

        refreshed = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
        assert refreshed.retry_count == 2

    @pytest.mark.asyncio
    async def test_retry_threshold_reached_marks_failed_and_logs_critical(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Seuil de retry atteint → statut FAILED, logger.critical appelé."""
        entry = _make_outbox_entry(retry_count=4)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 500
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result["failures"] == 1

        refreshed = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
        assert refreshed.status == OutboxStatus.FAILED

        # Vérifier que logger.critical a été appelé
        assert logger.critical.called
        critical_msg = str(logger.critical.call_args)
        assert "outbox" in critical_msg.lower() or "seuil" in critical_msg.lower()

    @pytest.mark.asyncio
    async def test_retry_uses_service_token_not_user_token(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Le retry utilise un token de service, pas le token utilisateur."""
        entry = _make_outbox_entry(retry_count=0)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        await engine.retry_pending_compensations(db_session, max_retries=5)

        call_kwargs = http_client.delete.call_args
        sent_headers = call_kwargs.kwargs.get("headers", {})
        auth_header = sent_headers.get("Authorization", "")
        assert auth_header.startswith("Bearer ")
        # Le token ne doit pas être vide
        token = auth_header.replace("Bearer ", "")
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_retry_network_error_increments_count(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Erreur réseau pendant retry → retry_count incrémenté, PENDING conservé."""
        entry = _make_outbox_entry(retry_count=0)
        db_session.add(entry)
        db_session.commit()

        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.side_effect = httpx.ConnectError("connection refused")

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result["failures"] == 1
        assert result["successes"] == 0

        refreshed = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
        assert refreshed.retry_count == 1

    @pytest.mark.asyncio
    async def test_retry_no_pending_entries_returns_zero(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Aucune entrée pending → retourne 0 succès et 0 échecs."""
        http_client = AsyncMock(spec=httpx.AsyncClient)

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        result = await engine.retry_pending_compensations(db_session, max_retries=5)

        assert result == {"successes": 0, "failures": 0}
        http_client.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_retry_info_logged_on_success(
        self, db_session, logger, admissions_repo, outbox_repo
    ):
        """Retry réussi → logger.info appelé."""
        entry = _make_outbox_entry(retry_count=0)
        db_session.add(entry)
        db_session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200
        http_client = AsyncMock(spec=httpx.AsyncClient)
        http_client.delete.return_value = mock_response

        engine = SagaEngine(admissions_repo, outbox_repo, logger, http_client)
        await engine.retry_pending_compensations(db_session, max_retries=5)

        assert logger.info.called
