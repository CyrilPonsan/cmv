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
