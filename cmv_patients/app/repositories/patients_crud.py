from abc import ABC, abstractmethod
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.sql.models import Patient
from typing import List


class PatientsRead(ABC):
    @abstractmethod
    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> tuple[List[Patient], int]:
        pass


class PatientsRepository(PatientsRead):
    @abstractmethod
    async def read_all_patients():
        pass


class PgPatientsRepository(PatientsRepository):
    async def read_all_patients(
        db: Session,
        page: int,
        limit: int,
        field: str = "nom",
        order: str = "asc",
    ):
        # Validation des paramètres d'entrée
        limit = min(max(1, limit), 50)  # Limite entre 1 et 50
        page = max(1, page)  # Page minimum de 1

        # Vérification du champ de tri
        allowed_fields = ["nom", "prenom", "date_de_naissance", "email"]
        field = field if field in allowed_fields else "nom"

        # Calcul de l'offset
        offset = (page - 1) * limit

        # Récupération du total
        total = db.query(func.count(Patient.id_patient)).scalar()

        # Vérification que la page demandée existe
        total_pages = (total + limit - 1) // limit
        if page > total_pages:
            page = 1
            offset = 0

        # Construction de la clause ORDER BY
        order_by_model = getattr(Patient, field)
        order_by_clause = (
            order_by_model.desc() if order.lower() == "desc" else order_by_model.asc()
        )

        # Exécution de la requête
        result = (
            db.query(Patient)
            .order_by(order_by_clause)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {"patients": result, "total": total, "total_pages": total_pages}
