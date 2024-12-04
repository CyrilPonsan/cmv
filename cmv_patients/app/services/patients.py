from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.patients_crud import PgPatientsRepository
from app.schemas.schemas import Patient


# Retourne une instance de la classe PgPatientsRepository
def get_patients_repository():
    return PgPatientsRepository()


# Initialisation du service Patients
def get_patients_service():
    return PatientsService(get_patients_repository())


class PatientsService:
    """Service gérant les opérations liées aux patients"""

    # Repository pour accéder aux données des patients
    patients_repository: PgPatientsRepository

    def __init__(self, patients_repository: PgPatientsRepository):
        """
        Initialise le service avec un repository de patients
        Args:
            patients_repository: Repository pour accéder aux données des patients
        """
        self.patients_repository = patients_repository

    async def read_all_patients(
        self,
        db: Session,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> dict:
        """
        Récupère la liste paginée de tous les patients
        Args:
            db: Session de base de données
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ sur lequel trier
            order: Ordre de tri (asc/desc)
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            dict: Dictionnaire contenant les patients et leur nombre total
        """
        # Appel au repository pour récupérer les patients avec pagination et tri
        return await self.patients_repository.read_all_patients(
            db=db, page=page, limit=limit, field=field, order=order
        )

    async def detail_patient(self, db: Session, patient_id: int):
        """
        Récupère les détails d'un patient spécifique
        Args:
            db: Session de base de données
            patient_id: ID du patient à récupérer
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            Patient: Les détails du patient demandé
        """
        # Appel au repository pour récupérer les détails d'un patient par son ID
        return await self.patients_repository.read_patient_by_id(
            db=db, patient_id=patient_id
        )

    async def search_patients(
        self,
        db: Session,
        search: str,
        page: int,
        limit: int,
        field: str,
        order: str,
    ) -> dict:
        """
        Recherche des patients selon des critères
        Args:
            db: Session de base de données
            search: Terme de recherche
            page: Numéro de la page
            limit: Nombre d'éléments par page
            field: Champ sur lequel trier
            order: Ordre de tri (asc/desc)
            user_id: ID de l'utilisateur faisant la requête
            role: Rôle de l'utilisateur
            request: Requête HTTP
        Returns:
            dict: Dictionnaire contenant les patients trouvés et leur nombre total
        """
        # Appel au repository pour rechercher des patients avec pagination et tri
        return await self.patients_repository.search_patients(
            db=db, search=search, page=page, limit=limit, field=field, order=order
        )

    async def create_patient(self, db: Session, data: Patient) -> Patient:
        """
        Crée un nouveau patient
        Args:
            db: Session de base de données
            patient: Données du patient à créer
        Returns:
            Patient: Le patient créé
        Raises:
            HTTPException: Si le patient existe déjà
        """
        # Vérification si le patient existe déjà
        if await self.patients_repository.check_patient_exists(db, data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="patient_already_exists"
            )
        # Création du patient via le repository
        return await self.patients_repository.create_patient(db, data)
