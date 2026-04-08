from datetime import datetime

from sqlalchemy.orm import Session

from app.sql.models import OutboxEntry, OutboxStatus


class PgOutboxRepository:
    """Repository CRUD pour la table outbox des compensations échouées."""

    async def create_entry(self, db: Session, entry: OutboxEntry) -> OutboxEntry:
        """
        Crée une nouvelle entrée dans la table outbox.
        Args:
            db: Session de base de données
            entry: Entrée outbox à persister
        Returns:
            OutboxEntry: L'entrée créée avec son ID généré
        """
        db.add(entry)
        db.flush()
        db.refresh(entry)
        return entry

    async def get_pending_entries(
        self, db: Session, max_retries: int
    ) -> list[OutboxEntry]:
        """
        Récupère les entrées outbox en attente de retry.
        Args:
            db: Session de base de données
            max_retries: Seuil maximum de tentatives
        Returns:
            list[OutboxEntry]: Entrées avec statut PENDING et retry_count < max_retries
        """
        return (
            db.query(OutboxEntry)
            .filter(
                OutboxEntry.status == OutboxStatus.PENDING,
                OutboxEntry.retry_count < max_retries,
            )
            .all()
        )

    async def update_status(
        self,
        db: Session,
        entry_id: int,
        status: str,
        increment_retries: bool = False,
    ) -> None:
        """
        Met à jour le statut d'une entrée outbox.
        Args:
            db: Session de base de données
            entry_id: ID de l'entrée à mettre à jour
            status: Nouveau statut (pending, completed, failed)
            increment_retries: Si True, incrémente le compteur de tentatives
        """
        entry = db.query(OutboxEntry).filter(OutboxEntry.id == entry_id).first()
        if entry is None:
            return

        entry.status = status
        entry.last_attempted_at = datetime.utcnow()

        if increment_retries:
            entry.retry_count += 1

        db.flush()
