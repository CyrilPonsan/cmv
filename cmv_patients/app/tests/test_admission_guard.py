"""Tests du garde-fou : empêcher la création d'admission si le patient en a déjà une."""

from datetime import datetime

import pytest
from fastapi import HTTPException

from app.sql.models import Admission, Patient


async def test_create_admission_rejected_when_admission_exists(
    ac, internal_token, db_session
):
    """POST /admissions retourne 400 patient_already_admitted si une admission existe."""
    patient = Patient(
        civilite="AUTRE",
        nom="Garde",
        prenom="Fou",
        adresse="1 rue test",
        code_postal="64000",
        ville="Pau",
        telephone="0600000000",
        date_de_naissance=datetime(1990, 1, 1),
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    admission = Admission(
        patient_id=patient.id_patient,
        ambulatoire=True,
        entree_le=datetime(2026, 1, 1),
        sortie_prevue_le=datetime(2026, 1, 5),
        ref_reservation=None,
    )
    db_session.add(admission)
    db_session.commit()

    resp = await ac.post(
        "/api/admissions",
        json={
            "patient_id": patient.id_patient,
            "ambulatoire": True,
            "entree_le": "2026-02-01T10:00:00",
            "sortie_prevue_le": "2026-02-05T10:00:00",
        },
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "patient_already_admitted"


async def test_create_admission_allowed_when_no_admission(
    ac, internal_token, db_session, httpx_mock
):
    """POST /admissions retourne 200 si le patient n'a pas d'admission."""
    patient = Patient(
        civilite="AUTRE",
        nom="Libre",
        prenom="Patient",
        adresse="1 rue test",
        code_postal="64000",
        ville="Pau",
        telephone="0600000000",
        date_de_naissance=datetime(1990, 1, 1),
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    resp = await ac.post(
        "/api/admissions",
        json={
            "patient_id": patient.id_patient,
            "ambulatoire": True,
            "entree_le": "2026-02-01T10:00:00",
            "sortie_prevue_le": "2026-02-05T10:00:00",
        },
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    # Ambulatoire = pas d'appel HTTP, donc pas besoin de mock chambres
    assert resp.status_code == 200


async def test_create_admission_404_when_patient_not_found(
    ac, internal_token, db_session
):
    """POST /admissions retourne 404 si le patient n'existe pas."""
    resp = await ac.post(
        "/api/admissions",
        json={
            "patient_id": 99999,
            "ambulatoire": True,
            "entree_le": "2026-02-01T10:00:00",
            "sortie_prevue_le": "2026-02-05T10:00:00",
        },
        headers={"Authorization": f"Bearer {internal_token}"},
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "patient_not_found"
