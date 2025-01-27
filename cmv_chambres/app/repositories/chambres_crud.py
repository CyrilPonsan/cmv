from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.reservation import Patient as CreatePatient, CreateReservation
from app.sql.models import Chambre, Status, Patient, Reservation


class ChambresCrud(ABC):
    """Classe abstraite définissant l'interface pour les opérations CRUD sur les chambres"""

    @abstractmethod
    async def get_chambre_by_id(self, db: Session, chambre_id: int) -> Chambre:
        """Récupère une chambre par son ID"""
        pass

    @abstractmethod
    async def get_available_room(self, db: Session, service_id: int) -> Chambre:
        """
        Méthode abstraite pour récupérer une chambre disponible pour un service
        Args:
            db (Session): Session de base de données
            service_id (int): Identifiant du service
        Returns:
            Chambre: Chambre disponible
        """
        pass

    @abstractmethod
    async def update_chambre_status(
        self, db: Session, chambre_id, chambre_status: Status
    ):
        """
        Méthode abstraite pour mettre à jour le statut d'une chambre
        """
        pass

    @abstractmethod
    async def update_chambre_patient(
        self, db: Session, chambre_id: int, patient: Patient
    ):
        """Met à jour le patient associé à une chambre"""
        pass

    @abstractmethod
    async def get_patient(self, db: Session, patient_id: int):
        """Récupère un patient par son ID"""
        pass

    @abstractmethod
    async def create_patient(self, db: Session, patient: CreatePatient):
        """Crée un nouveau patient"""
        pass

    @abstractmethod
    async def create_reservation(
        self,
        db: Session,
        chambre: Chambre,
        patient: Patient,
        reservation: CreateReservation,
    ):
        """Crée une nouvelle réservation"""
        pass


class ChambresRepository(ChambresCrud):
    """Implémentation abstraite de l'interface ChambresCrud"""

    @abstractmethod
    async def get_chambre_by_id(self, db: Session, chambre_id: int) -> Chambre:
        pass

    @abstractmethod
    async def get_available_room(self, db: Session, service_id: int) -> Chambre:
        pass

    @abstractmethod
    async def update_chambre_status(
        self, db: Session, chambre_id, chambre_status: Status
    ):
        pass

    @abstractmethod
    async def update_chambre_patient(
        self, db: Session, chambre_id: int, patient: Patient
    ):
        pass

    @abstractmethod
    async def get_patient(self, db: Session, patient_id: int):
        pass

    @abstractmethod
    async def create_patient(self, db: Session, patient: CreatePatient):
        pass

    @abstractmethod
    async def create_reservation(
        self,
        db: Session,
        chambre: Chambre,
        patient: Patient,
        reservation: CreateReservation,
    ):
        pass


class PgChambresRepository(ChambresRepository):
    """Implémentation PostgreSQL du repository de chambres"""

    async def get_chambre_by_id(self, db: Session, chambre_id: int) -> Chambre:
        """Récupère une chambre par son ID dans la base PostgreSQL"""
        return db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()

    async def get_available_room(self, db: Session, service_id: int) -> Chambre:
        """Récupère une chambre disponible pour un service donné"""
        return (
            db.query(Chambre)
            .filter(Chambre.service_id == service_id, Chambre.status == Status.LIBRE)
            .first()
        )

    async def update_chambre_status(
        self, db: Session, chambre_id, chambre_status: Status
    ):
        """Met à jour le statut d'une chambre"""
        chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
            )
        chambre.status = chambre_status
        db.commit()
        db.refresh(chambre)
        return chambre

    async def update_chambre_patient(
        self, db: Session, chambre_id: int, patient: Patient
    ):
        """Met à jour le patient associé à une chambre"""
        chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
            )
        chambre.patient = patient
        db.commit()
        db.refresh(chambre)
        return chambre

    async def get_patient(self, db: Session, patient_id: int):
        """Récupère un patient par son ID de référence"""
        return db.query(Patient).filter(Patient.ref_patient == patient_id).first()

    async def create_patient(self, db: Session, patient: CreatePatient):
        """Crée un nouveau patient dans la base de données"""
        patient = Patient(
            ref_patient=patient.id_patient,
            full_name=patient.full_name,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    async def create_reservation(
        self,
        db: Session,
        chambre: Chambre,
        patient: Patient,
        reservation: CreateReservation,
    ):
        """Crée une nouvelle réservation dans la base de données"""
        reservation = Reservation(
            patient=patient,
            chambre=chambre,
            entree_prevue=reservation.entree_prevue,
            sortie_prevue=reservation.sortie_prevue,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation
