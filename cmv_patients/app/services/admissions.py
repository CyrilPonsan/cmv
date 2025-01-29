# Import des dépendances FastAPI pour la gestion des erreurs HTTP
from fastapi import HTTPException, status

# Import du client HTTP asynchrone
import httpx

# Import de la session SQLAlchemy pour interagir avec la base de données
from sqlalchemy.orm import Session

# Import de la configuration du service des chambres
from app.utils.config import CHAMBRES_SERVICE

# Import des modèles SQLAlchemy pour les admissions et patients
from app.sql.models import Admission, Patient

# Import du schéma Pydantic pour la création d'une admission
from app.schemas.patients import CreateAdmission


class AdmissionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_admission(self, data: CreateAdmission):
        async with httpx.AsyncClient() as client:
            try:
                # Etape 1 : Si non ambulatoire, réserve une chambre
                chambre = None
                chambre_data = None
                if not data.ambulatoire:
                    response = await client.get(
                        f"{CHAMBRES_SERVICE}/chambres/{data.service_id}"
                    )
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="no_room_available",
                        )
                    chambre = response.json()

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
                            detail="server_failure",
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
                    ref_reservation=chambre_data["reservation_id"]
                    if chambre_data
                    else None,
                )

                self.db.add(admission)
                self.db.commit()
                self.db.refresh(admission)

                return admission

            except Exception as e:
                # Compensation en cas d'erreur
                if chambre_data:
                    await client.delete(
                        f"{CHAMBRES_SERVICE}/chambres/{chambre_data['reservation_id']}/{chambre_data['id_chambre']}/{chambre_data['patient_id']}/cancel",
                    )
                elif chambre is not None:
                    await client.put(
                        f"{CHAMBRES_SERVICE}/chambres/{chambre['id_chambre']}",
                    )

                self.db.rollback()
                if "no_room_available" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail="no_room_available",
                    )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"reservation_failed: {str(e)}",
                )


async def delete_admission(self, db: Session, admission_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        # Garder une trace des actions effectuées pour le rollback
        actions_done = {
            "reservation_cancelled": False,
            "chambre_status_updated": False,
            "admission_deleted": False,
        }

        try:
            # 1. Récupérer l'admission
            admission = await self.admissions_repository.get_admission_by_id(
                db, admission_id
            )
            if not admission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="admission_not_found"
                )

            # 2. Si non ambulatoire, annuler la réservation
            if not admission.ambulatoire and admission.ref_reservation:
                # Annuler la réservation
                response = await client.delete(
                    f"{CHAMBRES_SERVICE}/chambres/{admission.ref_reservation}/"
                    f"{admission.ref_chambre}/cancel"
                )
                if response.status_code not in (200, 404):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="failed_to_cancel_reservation",
                    )
                actions_done["reservation_cancelled"] = True
                actions_done["chambre_status_updated"] = True

            # 3. Supprimer l'admission
            await self.admissions_repository.delete_admission(db, admission_id)
            actions_done["admission_deleted"] = True

            db.commit()
            return {"message": "admission_deleted"}

        except Exception as e:
            db.rollback()

            # Compensation des actions effectuées en cas d'échec
            try:
                if actions_done["reservation_cancelled"]:
                    # Recréer la réservation
                    reservation_data = {
                        "patient": {
                            "id_patient": admission.patient_id,
                            "full_name": f"{admission.patient.prenom} {admission.patient.nom}",
                        },
                        "entree_prevue": str(admission.entree_le),
                        "sortie_prevue": str(admission.sortie_prevue_le),
                    }
                    await client.post(
                        f"{CHAMBRES_SERVICE}/chambres/{admission.ref_chambre}/reserver",
                        json=reservation_data,
                    )
            except Exception as compensation_error:
                # Log l'échec de la compensation
                print(
                    f"Failed to compensate actions for admission {admission_id}: {str(compensation_error)}"
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"delete_admission_failed: {str(e)}",
            )
