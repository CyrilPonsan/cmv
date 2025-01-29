from abc import ABC, abstractmethod
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.schemas.patients import CreatePatient
from app.sql.models import Admission, Patient
from typing import List
from fastapi import HTTPException, status


# Classe abstraite définissant l'interface pour les opérations CRUD sur les patients
class PatientCrud(ABC):
    """Interface abstraite définissant les méthodes CRUD pour les patients"""

    @abstractmethod
    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> tuple[List[Patient], int]:
        """Récupère tous les patients avec pagination"""
        pass

    @abstractmethod
    async def create_patient(self, db: Session, patient: Patient) -> Patient:
        """Crée un nouveau patient"""
        pass

    @abstractmethod
    async def check_patient_exists(self, db: Session, patient: Patient) -> bool:
        """Vérifie si un patient existe déjà"""
        pass

    @abstractmethod
    async def search_patients(
        self, db: Session, search: str, page: int, limit: int, field: str, order: str
    ) -> dict:
        """Recherche des patients selon des critères"""
        pass

    @abstractmethod
    async def read_patient_by_id(self, db: Session, patient_id: int) -> Patient:
        """Récupère un patient par son ID"""
        pass

    @abstractmethod
    async def update_patient(
        self, db: Session, patient_id: int, data: Patient
    ) -> Patient:
        """Met à jour les données d'un patient"""
        pass

    @abstractmethod
    async def delete_patient(self, db: Session, patient_id: int):
        """Supprime un patient"""
        pass


# Implémentation PostgreSQL du repository de patients
class PgPatientsRepository(PatientCrud):
    """Implémentation concrète du repository pour PostgreSQL"""

    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str = "nom",
        order: str = "asc",
    ) -> dict:
        """
        Récupère tous les patients avec pagination et tri
        Args:
            db: Session de base de données
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ de tri
            order: Ordre de tri (asc/desc)
        Returns:
            dict: Dictionnaire contenant les données et le total
        """
        return self.paginate_and_order(db, Patient, page, limit, field, order)

    async def create_patient(self, db: Session, patient: CreatePatient) -> Patient:
        """
        Crée un nouveau patient dans la base de données
        Args:
            db: Session de base de données
            patient: Données du patient à créer
        Returns:
            Patient: Le patient créé
        """
        # Création d'une instance Patient à partir des données reçues
        db_patient = Patient(**patient.model_dump())
        # Ajout à la session
        db.add(db_patient)
        # Validation des changements
        db.commit()
        # Rafraîchissement pour obtenir l'ID généré
        db.refresh(db_patient)
        print(
            f"DB_PATIENT : {db_patient.nom} {db_patient.prenom} {db_patient.id_patient}"
        )
        return db_patient

    async def check_patient_exists(self, db: Session, patient: Patient) -> bool:
        """
        Vérifie si un patient existe déjà avec les mêmes informations
        Args:
            db: Session de base de données
            patient: Patient à vérifier
        Returns:
            bool: True si le patient existe, False sinon
        """
        # Recherche d'un patient avec les mêmes nom, prénom et date de naissance
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
        """
        Met à jour les données d'un patient
        Args:
            db: Session de base de données
            patient_id: ID du patient à mettre à jour
            data: Nouvelles données du patient
        Returns:
            Patient: Le patient mis à jour
        Raises:
            HTTPException: Si le patient n'est pas trouvé
        """
        # Recherche du patient par son ID
        patient = db.query(Patient).filter(Patient.id_patient == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )
        # Mise à jour des attributs du patient
        for key, value in data.model_dump().items():
            setattr(patient, key, value)
        # Validation des changements
        db.commit()
        db.refresh(patient)
        return patient

    async def search_patients(
        self,
        db: Session,
        search: str,
        page: int,
        limit: int,
        field: str = "nom",
        order: str = "asc",
    ) -> dict:
        """
        Recherche des patients selon des critères
        Args:
            db: Session de base de données
            search: Terme de recherche
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ de tri
            order: Ordre de tri
        Returns:
            dict: Résultats de recherche paginés
        """
        # Création du filtre de recherche sur le nom
        filters = [Patient.nom.ilike(f"%{search}%")]
        return self.paginate_and_order(db, Patient, page, limit, field, order, filters)

    async def read_patient_by_id(self, db: Session, patient_id: int) -> Patient:
        """
        Récupère un patient par son ID avec sa dernière admission
        Args:
            db: Session de base de données
            patient_id: ID du patient
        Returns:
            Patient: Le patient trouvé avec sa dernière admission
        Raises:
            HTTPException: Si le patient n'est pas trouvé
        """
        # Recherche du patient par son ID avec jointure sur les admissions
        patient = db.query(Patient).filter(Patient.id_patient == patient_id).first()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )

        # Récupération de la dernière admission
        latest_admission = (
            db.query(Admission)
            .filter(Admission.patient_id == patient_id)
            .order_by(Admission.created_at.desc())
            .first()
        )

        # Ajout de la dernière admission au patient
        patient.latest_admission = latest_admission

        print(f"PATIENT : {patient.nom} {patient.prenom}")
        return patient

    def paginate_and_order(
        self, db, model, page, limit, field, order, filters=None
    ) -> dict:
        """
        Fonction utilitaire pour la pagination et le tri des résultats
        Args:
            db: Session de base de données
            model: Modèle SQLAlchemy
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ de tri
            order: Ordre de tri
            filters: Filtres additionnels
        Returns:
            dict: Résultats paginés et triés
        """
        # Validation des paramètres d'entrée
        limit = min(max(1, limit), 50)  # Limite entre 1 et 50
        page = max(1, page)  # Page minimum de 1

        # Calcul de l'offset pour la pagination
        offset = (page - 1) * limit

        # Récupération du nombre total d'enregistrements
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

        # Exécution de la requête paginée et triée
        query = db.query(model)
        if filters:
            query = query.filter(*filters)

        query = query.order_by(order_by_clause).offset(offset).limit(limit)
        result = query.all()

        return {"data": result, "total": total}

    async def delete_patient(self, db: Session, patient_id: int):
        """
        Supprime un patient de la base de données
        Args:
            db: Session de base de données
            patient_id: ID du patient à supprimer
        Returns:
            dict: Message de confirmation
        Raises:
            HTTPException: Si le patient n'est pas trouvé
        """
        query = db.query(Patient).filter(Patient.id_patient == patient_id).first()
        if not query:
            raise HTTPException(status_code=404, detail="patient_not_found")
        db.delete(query)
        db.commit()
        return {"message": "patient_deleted"}
