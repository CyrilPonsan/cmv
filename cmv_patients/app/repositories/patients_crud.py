from abc import ABC, abstractmethod
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.schemas.patients import CreatePatient
from app.sql.models import Patient
from typing import List
from fastapi import HTTPException, status


class PatientCrud(ABC):
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

    @abstractmethod
    async def create_patient(self, db: Session, patient: Patient) -> Patient:
        pass

    @abstractmethod
    async def check_patient_exists(self, db: Session, patient: Patient) -> bool:
        pass

    @abstractmethod
    async def search_patients(
        self, db: Session, search: str, page: int, limit: int, field: str, order: str
    ) -> dict:
        pass

    @abstractmethod
    async def read_patient_by_id(self, db: Session, patient_id: int) -> Patient:
        pass

    @abstractmethod
    async def update_patient(
        self, db: Session, patient_id: int, data: Patient
    ) -> Patient:
        pass


class PatientsRepository(PatientCrud):
    @abstractmethod
    async def read_all_patients(
        self, db: Session, page: int, limit: int, field: str, order: str
    ) -> dict:
        pass

    @abstractmethod
    async def read_patient_by_id(self, db: Session, patient_id: int) -> Patient:
        pass

    @abstractmethod
    async def create_patient(self, db: Session, patient: Patient) -> Patient:
        pass

    @abstractmethod
    async def check_patient_exists(self, db: Session, patient: Patient) -> bool:
        pass

    @abstractmethod
    async def search_patients(
        self, db: Session, search: str, page: int, limit: int, field: str, order: str
    ) -> dict:
        pass

    @abstractmethod
    async def update_patient(
        self, db: Session, patient_id: int, data: Patient
    ) -> Patient:
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

    async def create_patient(self, db: Session, patient: CreatePatient) -> Patient:
        db_patient = Patient(**patient.model_dump())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        print(
            f"DB_PATIENT : {db_patient.nom} {db_patient.prenom} {db_patient.id_patient}"
        )
        return db_patient

    async def check_patient_exists(self, db: Session, patient: Patient) -> bool:
        patient = (
            db.query(Patient)
            .filter(Patient.nom == patient.nom)
            .filter(Patient.prenom == patient.prenom)
            .filter(Patient.date_de_naissance == patient.date_de_naissance)
            .first()
        )
        return patient is not None

    async def update_patient(
        self, db: Session, patient_id: int, data: Patient
    ) -> Patient:
        patient = db.query(Patient).filter(Patient.id_patient == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )
        for key, value in data.model_dump().items():
            setattr(patient, key, value)
        db.commit()
        db.refresh(patient)
        return patient

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

    # Fonction de lecture d'un patient par son id
    async def read_patient_by_id(self, db: Session, patient_id: int) -> Patient:
        patient = db.query(Patient).filter(Patient.id_patient == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )
        print(f"PATIENT : {patient.nom} {patient.prenom}")
        return patient

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
