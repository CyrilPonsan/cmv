"""Router d'administration pour les opérations de maintenance du saga."""

import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.outbox_crud import PgOutboxRepository
from app.services.saga_engine import SagaEngine

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/outbox/retry")
async def retry_outbox_compensations(
    payload: Annotated[dict, Depends(check_authorization)],
    db: Session = Depends(get_db),
):
    """Rejoue les compensations pending de la table outbox.

    Endpoint protégé par authentification. Déclenche manuellement
    le retry des compensations échouées persistées dans l'outbox.

    Returns:
        dict avec les clés 'successes' et 'failures'
    """
    async with httpx.AsyncClient() as http_client:
        saga_engine = SagaEngine(
            admissions_repository=PgAdmissionsRepository(),
            outbox_repository=PgOutboxRepository(),
            logger=logging.getLogger("saga_engine"),
            http_client=http_client,
        )
        return await saga_engine.retry_pending_compensations(db=db)
