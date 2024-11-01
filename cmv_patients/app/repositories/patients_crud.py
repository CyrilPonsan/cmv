from abc import ABC, abstractmethod
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.sql.models import Patient
from typing import List
from fastapi import HTTPException, status


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
    # Fonction de lecture de tous les patients avec pagination et tri
    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str = "nom",
        order: str = "asc",
    ) -> dict:
        return self.paginate_and_order(db, Patient, page, limit, field, order)

    # Fonction de recherche de patients avec pagination et tri
    async def search_patients(
        self,
        db: Session,
        search: str,
        page: int,
        limit: int,
        field: str = "nom",
        order: str = "asc",
    ) -> dict:
        filters = [Patient.nom.ilike(f"%{search}%")]
        return self.paginate_and_order(db, Patient, page, limit, field, order, filters)

    # Fonction de pagination et de tri
    def paginate_and_order(
        self, db, model, page, limit, field, order, filters=None
    ) -> dict:
        # Validation des paramètres d'entrée
        limit = min(max(1, limit), 50)
        page = max(1, page)

        # Calcul de l'offset
        offset = (page - 1) * limit

        # Récupération du total
        query = db.query(func.count(model.id_patient))
        if filters:
            query = query.filter(*filters)
        total = query.scalar()

        # Vérification que la page demandée existe
        total_pages = (total + limit - 1) // limit
        if page > total_pages:
            page = 1
            offset = 0

        # Construction de la clause ORDER BY
        order_by_model = getattr(model, field)
        order_by_clause = (
            order_by_model.desc() if order.lower() == "desc" else order_by_model.asc()
        )

        # Exécution de la requête
        query = db.query(model)
        if filters:
            query = query.filter(*filters)

        query = query.order_by(order_by_clause).offset(offset).limit(limit)
        result = query.all()

        return {"data": result, "total": total}
