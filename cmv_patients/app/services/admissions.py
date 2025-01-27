from fastapi import HTTPException, status
import httpx
from sqlalchemy.orm import Session

from app.utils.config import CHAMBRES_SERVICE
from app.sql.models import Admission, Patient
from app.schemas.patients import CreateAdmission


class AdmissionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_admission(self, data: CreateAdmission):
        async with httpx.AsyncClient() as client:
            try:
                print(f"URL {CHAMBRES_SERVICE}")
                print(f"DATA{data}")
                # Etape 1 : Si non ambulatoire, réserve une chambre
                chambre_data = None
                print(f"AMBULATOIRE {data.ambulatoire}")
                if not data.ambulatoire:
                    print(f"SERVICE ID{data.service_id}")
                    print(f"{CHAMBRES_SERVICE}/chambres/{data.service_id}")
                    response = await client.get(
                        f"{CHAMBRES_SERVICE}/chambres/{data.service_id}"
                    )
                    print(f"STATUSCODE {response.status_code}")
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="dans le cul lulu",
                        )
                    chambre = response.json()

                    print(f"CHAMBRE{chambre}")

                    patient = (
                        self.db.query(Patient)
                        .filter(Patient.id_patient == data.patient_id)
                        .first()
                    )
                    if not patient:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="patient_not_found",
                        )
                    # Créer la réservation
                    reservation_data = {
                        "patient": {
                            "id_patient": data.patient_id,
                            "full_name": f"{patient.prenom} {patient.nom}",
                        },
                        "entree_prevue": str(data.entree_le),
                        "sortie_prevue": str(data.sortie_prevue_le),
                    }

                    response = await client.post(
                        f"{CHAMBRES_SERVICE}/chambres/{chambre['id_chambre']}/reserver",
                        json=reservation_data,
                    )
                    if response.status_code != 201:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="ooops",
                        )

                    chambre_data = response.json()

                # Etape 2 : Crée l'admission
                admission = Admission(
                    patient_id=data.patient_id,
                    ambulatoire=data.ambulatoire,
                    entree_le=str(data.entree_le),
                    sortie_prevue_le=str(data.sortie_prevue_le),
                    ref_chambre=chambre_data["id_chambre"] if chambre_data else None,
                    nom_chambre=chambre_data["nom"] if chambre_data else None,
                )

                self.db.add(admission)
                self.db.commit()
                self.db.refresh(admission)

                return admission

            except Exception as e:
                # Compensation en cas d'erreur
                if chambre_data:
                    await client.delete(
                        f"{CHAMBRES_SERVICE}/chambres/{chambre_data['id_chambre']}/rerserver",
                    )
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"reservation_failed: {str(e)}",
                )
