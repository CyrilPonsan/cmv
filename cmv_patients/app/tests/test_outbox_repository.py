"""Tests unitaires pour PgOutboxRepository.

Valide les opérations CRUD de la table outbox : création d'entrées,
filtrage des entrées pending par retry_count, et mise à jour de statut
avec incrémentation du retry_count.

Validates: Requirements 3.1
"""

from datetime import datetime

import pytest

from app.repositories.outbox_crud import PgOutboxRepository
from app.sql.models import OutboxEntry, OutboxStatus


@pytest.fixture
def outbox_repo():
    """Instance du repository outbox."""
    return PgOutboxRepository()


# ---------------------------------------------------------------------------
# Création d'une entrée outbox
# ---------------------------------------------------------------------------


async def test_create_entry_persists_and_returns(outbox_repo, db_session):
    """Validates: Requirements 3.1

    create_entry doit persister l'entrée en base et retourner l'objet
    avec un id généré.
    """
    entry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"reservation_id": 42, "admission_id": 10},
        retry_count=0,
        status=OutboxStatus.PENDING,
    )

    result = await outbox_repo.create_entry(db_session, entry)

    assert result.id is not None
    assert result.compensation_type == "cancel_reservation"
    assert result.payload == {"reservation_id": 42, "admission_id": 10}
    assert result.retry_count == 0
    assert result.status == OutboxStatus.PENDING


async def test_create_entry_is_queryable(outbox_repo, db_session):
    """Validates: Requirements 3.1

    Après create_entry, l'entrée doit être retrouvable via une query directe.
    """
    entry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"reservation_id": 7},
    )

    created = await outbox_repo.create_entry(db_session, entry)

    found = db_session.query(OutboxEntry).filter(OutboxEntry.id == created.id).first()
    assert found is not None
    assert found.compensation_type == "cancel_reservation"
    assert found.payload == {"reservation_id": 7}


# ---------------------------------------------------------------------------
# Filtrage des entrées pending par retry_count
# ---------------------------------------------------------------------------


async def test_get_pending_entries_returns_only_pending(outbox_repo, db_session):
    """Validates: Requirements 3.1

    get_pending_entries ne doit retourner que les entrées avec statut PENDING.
    """
    pending = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 1},
        status=OutboxStatus.PENDING,
        retry_count=0,
    )
    completed = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 2},
        status=OutboxStatus.COMPLETED,
        retry_count=0,
    )
    failed = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 3},
        status=OutboxStatus.FAILED,
        retry_count=5,
    )

    db_session.add_all([pending, completed, failed])
    db_session.flush()

    results = await outbox_repo.get_pending_entries(db_session, max_retries=5)

    assert len(results) == 1
    assert results[0].payload == {"id": 1}


async def test_get_pending_entries_filters_by_max_retries(outbox_repo, db_session):
    """Validates: Requirements 3.1

    get_pending_entries ne doit retourner que les entrées pending dont
    retry_count < max_retries.
    """
    low_retry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 1},
        status=OutboxStatus.PENDING,
        retry_count=2,
    )
    at_threshold = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 2},
        status=OutboxStatus.PENDING,
        retry_count=5,
    )
    over_threshold = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 3},
        status=OutboxStatus.PENDING,
        retry_count=7,
    )

    db_session.add_all([low_retry, at_threshold, over_threshold])
    db_session.flush()

    results = await outbox_repo.get_pending_entries(db_session, max_retries=5)

    assert len(results) == 1
    assert results[0].payload == {"id": 1}
    assert results[0].retry_count == 2


async def test_get_pending_entries_returns_empty_when_none_match(
    outbox_repo, db_session
):
    """Validates: Requirements 3.1

    get_pending_entries retourne une liste vide quand aucune entrée ne
    correspond aux critères.
    """
    results = await outbox_repo.get_pending_entries(db_session, max_retries=5)
    assert results == []


# ---------------------------------------------------------------------------
# Mise à jour de statut et incrémentation du retry_count
# ---------------------------------------------------------------------------


async def test_update_status_changes_status(outbox_repo, db_session):
    """Validates: Requirements 3.1

    update_status doit changer le statut de l'entrée et mettre à jour
    last_attempted_at.
    """
    entry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 1},
        status=OutboxStatus.PENDING,
        retry_count=0,
    )
    db_session.add(entry)
    db_session.flush()
    db_session.refresh(entry)

    await outbox_repo.update_status(
        db_session, entry.id, OutboxStatus.COMPLETED
    )

    updated = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
    assert updated.status == OutboxStatus.COMPLETED
    assert updated.last_attempted_at is not None


async def test_update_status_increments_retry_count(outbox_repo, db_session):
    """Validates: Requirements 3.1

    update_status avec increment_retries=True doit incrémenter retry_count.
    """
    entry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 1},
        status=OutboxStatus.PENDING,
        retry_count=2,
    )
    db_session.add(entry)
    db_session.flush()
    db_session.refresh(entry)

    await outbox_repo.update_status(
        db_session, entry.id, OutboxStatus.PENDING, increment_retries=True
    )

    updated = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
    assert updated.retry_count == 3
    assert updated.status == OutboxStatus.PENDING


async def test_update_status_without_increment_keeps_retry_count(
    outbox_repo, db_session
):
    """Validates: Requirements 3.1

    update_status sans increment_retries ne doit pas modifier retry_count.
    """
    entry = OutboxEntry(
        compensation_type="cancel_reservation",
        payload={"id": 1},
        status=OutboxStatus.PENDING,
        retry_count=3,
    )
    db_session.add(entry)
    db_session.flush()
    db_session.refresh(entry)

    await outbox_repo.update_status(
        db_session, entry.id, OutboxStatus.FAILED
    )

    updated = db_session.query(OutboxEntry).filter(OutboxEntry.id == entry.id).first()
    assert updated.retry_count == 3
    assert updated.status == OutboxStatus.FAILED


async def test_update_status_nonexistent_entry_does_nothing(outbox_repo, db_session):
    """Validates: Requirements 3.1

    update_status sur un entry_id inexistant ne doit pas lever d'exception.
    """
    await outbox_repo.update_status(
        db_session, 99999, OutboxStatus.COMPLETED
    )
    # No exception raised — pass
