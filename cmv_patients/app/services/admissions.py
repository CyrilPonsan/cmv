from fastapi import HTTPException, status
import httpx
from sqlalchemy.orm import Session

from app.schemas.schemas import CreateAdmission
from app.utils.config import CHAMBRES_API_URL
from app.sql.models import Admission


class AdmissionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_admission(self, data: CreateAdmission):
        async with httpx.AsyncClient() as client:
            try:
                # Etape 1 : Si non ambulatoire, réserve une chambre
                chambre_data = None
                if not data.ambulatoire:
                    response = await client.get(
                        f"{CHAMBRES_API_URL}/chambres/reserve",
                        params={"service_id": data.service_id},
                    )
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="no_room_available",
                        )
                    chambre = response.json()

                    # Créer la réservation
                    reservation_data = {
                        "patient": {
                            "id_patient": data.patient_id,
                            "full_name": f"{data.patient.prenom} {data.patient.nom}",
                        },
                        "entree_prevue_le": data.entree_le,
                        "sortie_prevue_le": data.sortie_prevue_le,
                    }

                    response = await client.post(
                        f"{CHAMBRES_API_URL}/chambres/{chambre['id_chambre']}/rerserver",
                        json=reservation_data,
                    )
                    if response.status_code != 201:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="reservation_failed",
                        )

                    chambre_data = response.json()

                # Etape 2 : Crée l'admission
                admission = Admission(
                    patient_id=data.patient_id,
                    ambulatoire=data.ambulatoire,
                    entree_le=data.entree_le,
                    sortie_prevue_le=data.sortie_prevue_le,
                    ref_chambre=chambre_data["id_chambre"] if chambre_data else None,
                    nom_chambre=chambre_data["nom_chambre"] if chambre_data else None,
                )

                self.db.add(admission)
                await self.db.commit()
                await self.db.refresh(admission)

                return admission

            except Exception as e:
                # Compensation en cas d'erreur
                if chambre_data:
                    await client.delete(
                        f"{CHAMBRES_API_URL}/chambres/{chambre_data['id_chambre']}/rerserver",
                    )
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"reservation_failed: {str(e)}",
                )
