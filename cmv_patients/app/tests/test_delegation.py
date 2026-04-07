"""Tests unitaires pour la délégation — task 5.3.

Vérifie que :
- PatientsService.delete_patient délègue à AdmissionService.delete_admission
- Aucun print() n'existe dans le module SagaEngine
- Edge case : admission ambulatoire sans réservation → pas d'appel HTTP
- Edge case : admission inexistante → HTTPException 404

Validates: Requirements 2.1, 2.2, 1.3
"""

import inspect
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.documents_crud import PgDocumentsRepository
from app.repositories.patients_crud import PgPatientsRepository
from app.services.admissions import AdmissionService
from app.services.patients import PatientsService
from app.sql.models import Admission, Patient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_patient(db_session, patient_id=1) -> Patient:
    """Insère un patient minimal en base et le retourne."""
    patient = Patient(
        id_patient=patient_id,
        civilite="AUTRE",
        nom="Dupont",
        prenom="Jean",
        adresse="1 rue test",
        code_postal="75000",
        ville="Paris",
        telephone="0600000000",
        date_de_naissance=datetime(1990, 1, 1),
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


def _make_admission(
    db_session,
    patient_id=1,
    admission_id=None,
    ambulatoire=False,
    ref_reservation=42,
) -> Admission:
    """Insère une admission en base et la retourne."""
    admission = Admission(
        patient_id=patient_id,
        ambulatoire=ambulatoire,
        ref_reservation=ref_reservation,
        entree_le=datetime(2026, 1, 1),
        sortie_prevue_le=datetime(2026, 1, 5),
    )
    if admission_id is not None:
        admission.id_admission = admission_id
    db_session.add(admission)
    db_session.commit()
    db_session.refresh(admission)
    return admission


def _build_patients_service(admission_service: AdmissionService) -> PatientsService:
    """Construit un PatientsService avec les vrais repos et un admission_service injecté."""
    return PatientsService(
        patients_repository=PgPatientsRepository(),
        documents_repository=PgDocumentsRepository(),
        admissions_repository=PgAdmissionsRepository(),
        admission_service=admission_service,
    )


# ---------------------------------------------------------------------------
# 1. PatientsService.delete_patient délègue à AdmissionService.delete_admission
#    Validates: Requirements 2.1, 2.2
# ---------------------------------------------------------------------------

class TestDeletePatientDelegation:
    """Vérifie que delete_patient appelle admission_service.delete_admission
    pour chaque admission du patient."""

    @pytest.mark.asyncio
    async def test_delete_patient_calls_delete_admission_for_each_admission(
        self, db_session
    ):
        """delete_patient doit appeler admission_service.delete_admission
        une fois par admission."""
        patient = _make_patient(db_session, patient_id=1)
        adm1 = _make_admission(db_session, patient_id=patient.id_patient, ambulatoire=False, ref_reservation=10)
        adm2 = _make_admission(db_session, patient_id=patient.id_patient, ambulatoire=True, ref_reservation=None)

        expected_ids = sorted([adm1.id_admission, adm2.id_admission])

        # Side effect that actually removes the admission from DB so the
        # subsequent patient delete (CASCADE) doesn't hit a NOT NULL constraint.
        async def _fake_delete(db, admission_id, payload, request):
            db.query(Admission).filter(
                Admission.id_admission == admission_id
            ).delete()
            db.flush()
            return {"message": "admission_deleted"}

        mock_admission_service = AsyncMock(spec=AdmissionService)
        mock_admission_service.delete_admission = AsyncMock(side_effect=_fake_delete)

        service = _build_patients_service(mock_admission_service)

        fake_request = MagicMock()
        await service.delete_patient(db_session, patient.id_patient, "token-xyz", fake_request)

        assert mock_admission_service.delete_admission.call_count == 2

        called_admission_ids = sorted(
            call.args[1] for call in mock_admission_service.delete_admission.call_args_list
        )
        assert called_admission_ids == expected_ids

    @pytest.mark.asyncio
    async def test_delete_patient_passes_correct_args_to_delete_admission(
        self, db_session
    ):
        """delete_patient transmet db, admission_id, internal_payload et request."""
        patient = _make_patient(db_session, patient_id=1)
        adm = _make_admission(db_session, patient_id=patient.id_patient)

        async def _fake_delete(db, admission_id, payload, request):
            db.query(Admission).filter(
                Admission.id_admission == admission_id
            ).delete()
            db.flush()
            return {"message": "admission_deleted"}

        mock_admission_service = AsyncMock(spec=AdmissionService)
        mock_admission_service.delete_admission = AsyncMock(side_effect=_fake_delete)

        service = _build_patients_service(mock_admission_service)

        fake_request = MagicMock()
        await service.delete_patient(db_session, patient.id_patient, "my-token", fake_request)

        call_args = mock_admission_service.delete_admission.call_args_list[0]
        assert call_args.args[0] is db_session
        assert call_args.args[1] == adm.id_admission
        assert call_args.args[2] == "my-token"
        assert call_args.args[3] is fake_request


# ---------------------------------------------------------------------------
# 2. Aucun print() dans le module SagaEngine
#    Validates: Requirement 1.3
# ---------------------------------------------------------------------------

class TestNoPrintInSagaEngine:
    """Le module saga_engine.py ne doit contenir aucun appel print()."""

    def test_no_print_in_saga_engine_source(self):
        import app.services.saga_engine as module

        source = inspect.getsource(module)
        lines = source.split("\n")
        # Filtrer les commentaires et docstrings simples
        code_lines = [
            line
            for line in lines
            if line.strip()
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ]
        code = "\n".join(code_lines)
        assert "print(" not in code, (
            "Le module saga_engine.py contient un appel print(). "
            "Utilisez le logger structuré à la place."
        )


# ---------------------------------------------------------------------------
# 3. Edge case : admission ambulatoire sans réservation → pas d'appel HTTP
#    Validates: Requirements 2.1, 2.3
# ---------------------------------------------------------------------------

class TestAmbulatoryNoHttpCall:
    """Une admission ambulatoire (ambulatoire=True, ref_reservation=None)
    ne doit déclencher aucun appel HTTP vers le service chambres."""

    @pytest.mark.asyncio
    async def test_ambulatory_admission_no_http_call_via_admission_service(
        self, db_session
    ):
        """delete_admission sur une admission ambulatoire ne fait pas d'appel HTTP."""
        patient = _make_patient(db_session, patient_id=1)
        adm = _make_admission(
            db_session,
            patient_id=patient.id_patient,
            ambulatoire=True,
            ref_reservation=None,
        )

        admission_service = AdmissionService(
            admissions_repository=PgAdmissionsRepository()
        )

        fake_request = MagicMock()
        fake_request.headers = {
            "X-Real-IP": "127.0.0.1",
            "X-Forwarded-For": "127.0.0.1",
        }

        with patch("app.services.admissions.httpx.AsyncClient") as MockClient:
            mock_http = AsyncMock()
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await admission_service.delete_admission(
                db_session, adm.id_admission, "token-abc", fake_request
            )

            assert result == {"message": "admission_deleted"}
            mock_http.delete.assert_not_called()


# ---------------------------------------------------------------------------
# 4. Edge case : admission inexistante → HTTPException 404
#    Validates: Requirement 2.1
# ---------------------------------------------------------------------------

class TestNonExistentAdmission:
    """Tenter de supprimer une admission inexistante doit lever HTTPException 404."""

    @pytest.mark.asyncio
    async def test_delete_nonexistent_admission_raises_404(self, db_session):
        admission_service = AdmissionService(
            admissions_repository=PgAdmissionsRepository()
        )

        fake_request = MagicMock()
        fake_request.headers = {}

        with pytest.raises(HTTPException) as exc_info:
            await admission_service.delete_admission(
                db_session, 99999, "token", fake_request
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "admission_not_found"
