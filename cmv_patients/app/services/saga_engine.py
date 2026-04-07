"""SagaEngine — orchestre le saga de suppression d'admission avec compensation."""

import logging
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.orm import Session

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.outbox_crud import PgOutboxRepository
from app.sql.models import Admission, OutboxEntry, OutboxStatus
from app.utils.config import ALGORITHM, CHAMBRES_SECRET_KEY, CHAMBRES_SERVICE


class SagaEngine:
    """Orchestre les étapes du saga de suppression d'admission.

    Responsable du logging structuré, de la gestion transactionnelle
    et de l'insertion outbox en cas d'échec de compensation.
    """

    def __init__(
        self,
        admissions_repository: PgAdmissionsRepository,
        outbox_repository: PgOutboxRepository,
        logger: logging.Logger,
        http_client: httpx.AsyncClient,
    ):
        self.admissions_repository = admissions_repository
        self.outbox_repository = outbox_repository
        self.logger = logger
        self.http_client = http_client

    async def execute_delete_admission(
        self,
        db: Session,
        admission: Admission,
        headers: dict,
    ) -> dict:
        """Orchestre la suppression d'une admission avec compensation.

        Pour les admissions non-ambulatoires avec réservation, tente d'abord
        d'annuler la réservation via HTTP. En cas d'échec, insère dans l'outbox
        puis rollback et lève une HTTPException 400.

        Si la compensation réussit (ou n'est pas nécessaire), supprime
        l'admission et commit atomiquement.
        """
        try:
            # Étape 1 : Annuler la réservation si nécessaire
            if not admission.ambulatoire and admission.ref_reservation:
                cancel_succeeded = await self._cancel_reservation(
                    db, admission, headers
                )
                if not cancel_succeeded:
                    # L'outbox a été insérée dans _cancel_reservation,
                    # on rollback tout et on lève une erreur
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="failed_to_cancel_reservation",
                    )

            # Étape 2 : Supprimer l'admission (flush, pas commit)
            db.query(Admission).filter(
                Admission.id_admission == admission.id_admission
            ).delete()
            db.flush()

            # Étape 3 : Commit atomique (admission + éventuel outbox)
            db.commit()

            self.logger.info(
                "Admission %s supprimée avec succès",
                admission.id_admission,
            )
            return {"message": "admission_deleted"}

        except HTTPException:
            raise

        except Exception as e:
            db.rollback()
            self.logger.error(
                "Échec du saga de suppression pour l'admission %s : %s",
                admission.id_admission,
                str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"delete_admission_failed: {str(e)}",
            )

    async def _cancel_reservation(
        self,
        db: Session,
        admission: Admission,
        headers: dict,
    ) -> bool:
        """Tente d'annuler la réservation. Insère dans outbox si échec.

        Returns:
            True si la compensation a réussi (200 ou 404).
            False si la compensation a échoué (outbox insérée).
        """
        endpoint = f"/chambres/{admission.ref_reservation}/cancel"
        url = f"{CHAMBRES_SERVICE}{endpoint}"

        http_headers = {
            "Authorization": headers.get("Authorization", ""),
            "X-Real-IP": headers.get("X-Real-IP", "unknown"),
            "X-Forwarded-For": headers.get("X-Forwarded-For", "unknown"),
        }

        try:
            response = await self.http_client.delete(url, headers=http_headers)

            if response.status_code in (200, 404):
                self.logger.info(
                    "Compensation réussie : annulation réservation %s "
                    "pour admission %s (status=%s)",
                    admission.ref_reservation,
                    admission.id_admission,
                    response.status_code,
                )
                return True

            # Code HTTP inattendu → échec
            error_msg = (
                f"HTTP {response.status_code} lors de l'annulation "
                f"de la réservation {admission.ref_reservation}"
            )
            self.logger.error(
                "Compensation échouée : annulation réservation %s "
                "pour admission %s — %s",
                admission.ref_reservation,
                admission.id_admission,
                error_msg,
            )

        except (httpx.ConnectError, httpx.TimeoutException, Exception) as exc:
            error_msg = str(exc)
            self.logger.error(
                "Compensation échouée : annulation réservation %s "
                "pour admission %s — %s",
                admission.ref_reservation,
                admission.id_admission,
                error_msg,
            )

        # Insérer dans l'outbox pour retry ultérieur
        outbox_entry = OutboxEntry(
            compensation_type="cancel_reservation",
            payload={
                "reservation_id": admission.ref_reservation,
                "admission_id": admission.id_admission,
                "chambres_service_url": CHAMBRES_SERVICE,
                "endpoint": endpoint,
            },
            retry_count=0,
        )
        await self.outbox_repository.create_entry(db, outbox_entry)

        return False

    def _generate_service_token(self) -> str:
        """Génère un token JWT de service interne pour les retries outbox."""
        payload = {
            "user_id": 0,
            "role": "service",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "source": "api_patients",
        }
        return jwt.encode(payload, CHAMBRES_SECRET_KEY, algorithm=ALGORITHM)

    async def retry_pending_compensations(
        self,
        db: Session,
        max_retries: int = 5,
    ) -> dict:
        """Rejoue les compensations pending de la table outbox.

        Récupère les entrées pending dont le retry_count < max_retries,
        tente la compensation HTTP pour chacune, et met à jour le statut.

        Args:
            db: Session de base de données
            max_retries: Seuil maximum de tentatives avant marquage FAILED

        Returns:
            dict avec les clés 'successes' et 'failures' (compteurs)
        """
        entries = await self.outbox_repository.get_pending_entries(db, max_retries)
        successes = 0
        failures = 0

        service_token = self._generate_service_token()

        for entry in entries:
            endpoint = entry.payload.get("endpoint", "")
            chambres_service_url = entry.payload.get(
                "chambres_service_url", CHAMBRES_SERVICE
            )
            url = f"{chambres_service_url}{endpoint}"

            http_headers = {
                "Authorization": f"Bearer {service_token}",
            }

            try:
                response = await self.http_client.delete(url, headers=http_headers)

                if response.status_code in (200, 404):
                    await self.outbox_repository.update_status(
                        db, entry.id, OutboxStatus.COMPLETED
                    )
                    successes += 1
                    self.logger.info(
                        "Retry compensation réussie pour l'entrée outbox %s "
                        "(endpoint=%s, status=%s)",
                        entry.id,
                        endpoint,
                        response.status_code,
                    )
                    continue

                # Code HTTP inattendu → échec
                error_msg = f"HTTP {response.status_code}"

            except (httpx.ConnectError, httpx.TimeoutException, Exception) as exc:
                error_msg = str(exc)

            # Échec : incrémenter retry_count
            await self.outbox_repository.update_status(
                db, entry.id, OutboxStatus.PENDING, increment_retries=True
            )
            db.flush()
            db.refresh(entry)

            failures += 1

            if entry.retry_count >= max_retries:
                await self.outbox_repository.update_status(
                    db, entry.id, OutboxStatus.FAILED
                )
                self.logger.critical(
                    "Seuil de retry atteint pour l'entrée outbox %s "
                    "(retry_count=%s, max_retries=%s, endpoint=%s) — %s",
                    entry.id,
                    entry.retry_count,
                    max_retries,
                    endpoint,
                    error_msg,
                )
            else:
                self.logger.error(
                    "Retry compensation échouée pour l'entrée outbox %s "
                    "(retry_count=%s, endpoint=%s) — %s",
                    entry.id,
                    entry.retry_count,
                    endpoint,
                    error_msg,
                )

        db.commit()

        return {"successes": successes, "failures": failures}
