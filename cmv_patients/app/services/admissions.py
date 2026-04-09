import logging

import httpx
from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.repositories.admissions_crud import PgAdmissionsRepository
from app.repositories.outbox_crud import PgOutboxRepository
from app.schemas.patients import CreateAdmission
from app.schemas.user import InternalPayload
from app.services.saga_engine import SagaEngine
from app.sql.models import Admission
from app.utils.config import CHAMBRES_SERVICE
from app.utils.logging_setup import LoggerSetup

logger = LoggerSetup()


def get_admissions_repository():
    return PgAdmissionsRepository()


def get_outbox_repository():
    return PgOutboxRepository()


def get_admissions_service():
    return AdmissionService(admissions_repository=get_admissions_repository())


class AdmissionService:
    admissions_repository: PgAdmissionsRepository

    def __init__(self, admissions_repository: PgAdmissionsRepository):
        self.admissions_repository = admissions_repository

    async def get_admission(self, db: Session, admission_id):
        admission = await self.admissions_repository.get_admission_by_id(
            db, admission_id
        )
        if not admission:
            raise HTTPException(status_code=404, detail="not_found")
        return admission

    async def create_admission(
        self,
        db: Session,
        data: CreateAdmission,
        internal_payload: str,
        request,
    ):
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For", "unknown"
        )
        headers = {
            "Authorization": f"Bearer {internal_payload}",
            "X-Real-IP": client_ip,
            "X-Forwarded-For": client_ip,
        }

        reservation = None

        async with httpx.AsyncClient() as client:
            try:
                # Etape 1 : Si non ambulatoire, réserver une chambre
                if not data.ambulatoire:
                    reservation = await self._reserve_room(client, data, headers)

                # Etape 2 : Créer l'admission en base
                admission = Admission(
                    patient_id=data.patient_id,
                    ambulatoire=data.ambulatoire,
                    entree_le=data.entree_le,
                    sortie_prevue_le=data.sortie_prevue_le,
                    ref_reservation=reservation["reservation_id"]
                    if reservation
                    else None,
                )
                admission = await self.admissions_repository.create_admission(
                    db, admission
                )
                return admission

            except HTTPException:
                # Compensation si la réservation a été créée
                if reservation:
                    await self._compensate_reservation(client, reservation, headers)
                raise

            except Exception as e:
                if reservation:
                    await self._compensate_reservation(client, reservation, headers)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

    async def delete_admission(
        self, db: Session, admission_id: int, internal_payload: str, request
    ):
        admission = await self.admissions_repository.get_admission_by_id(
            db, admission_id
        )
        if not admission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="admission_not_found"
            )

        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For", "unknown"
        )
        headers = {
            "Authorization": f"Bearer {internal_payload}",
            "X-Real-IP": client_ip,
            "X-Forwarded-For": client_ip,
        }

        async with httpx.AsyncClient() as http_client:
            saga_engine = SagaEngine(
                admissions_repository=self.admissions_repository,
                outbox_repository=get_outbox_repository(),
                logger=logging.getLogger("saga_engine"),
                http_client=http_client,
            )
            return await saga_engine.execute_delete_admission(
                db=db,
                admission=admission,
                headers=headers,
            )

    # --- Méthodes privées ---

    async def _reserve_room(
        self, client: httpx.AsyncClient, data: CreateAdmission, headers: dict
    ) -> dict:
        """Appelle l'API chambres pour réserver une chambre. Retourne le dict de réservation."""
        response = await client.post(
            f"{CHAMBRES_SERVICE}/chambres/{data.service_id}/reserver",
            headers=headers,
            json={
                "patient_id": data.patient_id,
                "entree_prevue": data.entree_le.isoformat(),
                "sortie_prevue": data.sortie_prevue_le.isoformat(),
            },
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="no_room_available"
            )
        if response.status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="reservation_failed",
            )
        return response.json()

    async def _compensate_reservation(
        self, client: httpx.AsyncClient, reservation: dict, headers: dict
    ):
        """Compensation : annule la réservation créée en cas d'échec."""
        try:
            reservation_id = reservation.get("reservation_id", 0)
            chambre_id = reservation.get("chambre_id", 0)
            await client.delete(
                f"{CHAMBRES_SERVICE}/chambres/{reservation_id}/{chambre_id}/cancel",
                headers=headers,
            )
        except Exception as e:
            print(f"Compensation failed: {e}")
