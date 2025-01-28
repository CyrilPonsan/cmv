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

    @abstractmethod
    async def get_reservation_by_id(self, db: Session, reservation_id: int):
        """Récupère une réservation par son ID"""
        pass

    @abstractmethod
    async def cancel_reservation(self, db: Session, reservation_id: int):
        """Annule une réservation"""
        pass

    @abstractmethod
    async def get_reservations(self, db: Session, patient_id: int):
        """Récupère les réservations d'un patient"""
        pass

    @abstractmethod
    async def delete_patient(self, db: Session, patient_id: int):
        """Supprime un patient"""
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

    @abstractmethod
    async def cancel_reservation(self, db: Session, reservation_id: int):
        """Annule une réservation"""
        pass

    @abstractmethod
    async def get_reservation_by_id(self, db: Session, reservation_id: int):
        """Récupère une réservation par son ID"""
        pass

    @abstractmethod
    async def get_reservations(self, db: Session, patient_id: int):
        """Récupère les réservations d'un patient"""
        pass

    @abstractmethod
    async def delete_patient(self, db: Session, patient_id: int):
        """Supprime un patient"""
        pass


class PgChambresRepository(ChambresRepository):
    """Implémentation PostgreSQL du repository de chambres"""

    async def get_chambre_by_id(self, db: Session, chambre_id: int) -> Chambre:
        """
        Récupère une chambre par son ID dans la base PostgreSQL

        Args:
            db (Session): Session de base de données
            chambre_id (int): ID de la chambre à récupérer

        Returns:
            Chambre: La chambre trouvée ou None si non trouvée
        """
        # Requête pour récupérer une chambre par son ID
        return db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()

    async def get_available_room(self, db: Session, service_id: int) -> Chambre:
        """
        Récupère une chambre disponible pour un service donné

        Args:
            db (Session): Session de base de données
            service_id (int): ID du service pour lequel chercher une chambre

        Returns:
            Chambre: La première chambre libre trouvée ou None si aucune disponible
        """
        # Requête pour trouver une chambre libre dans le service spécifié
        return (
            db.query(Chambre)
            .filter(Chambre.service_id == service_id, Chambre.status == Status.LIBRE)
            .first()
        )

    async def update_chambre_status(
        self, db: Session, chambre_id, chambre_status: Status
    ):
        """
        Met à jour le statut d'une chambre

        Args:
            db (Session): Session de base de données
            chambre_id (int): ID de la chambre à mettre à jour
            chambre_status (Status): Nouveau statut à appliquer

        Returns:
            Chambre: La chambre mise à jour

        Raises:
            HTTPException: Si la chambre n'est pas trouvée
        """
        # Recherche de la chambre dans la base de données
        chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
            )

        # Mise à jour du statut
        chambre.status = chambre_status

        # Sauvegarde des modifications
        db.commit()
        db.refresh(chambre)
        return chambre

    async def update_chambre_patient(
        self, db: Session, chambre_id: int, patient: Patient
    ):
        """
        Met à jour le patient associé à une chambre

        Args:
            db (Session): Session de base de données
            chambre_id (int): ID de la chambre à mettre à jour
            patient (Patient): Patient à associer à la chambre

        Returns:
            Chambre: La chambre mise à jour

        Raises:
            HTTPException: Si la chambre n'est pas trouvée
        """
        # Recherche de la chambre dans la base de données
        chambre = db.query(Chambre).filter(Chambre.id_chambre == chambre_id).first()
        if not chambre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chambre_not_found"
            )

        # Association du patient à la chambre
        chambre.patient = patient

        # Sauvegarde des modifications
        db.commit()
        db.refresh(chambre)
        return chambre

    async def get_patient(self, db: Session, patient_id: int):
        """
        Récupère un patient par son ID de référence

        Args:
            db (Session): Session de base de données
            patient_id (int): ID du patient à récupérer

        Returns:
            Patient: Le patient trouvé ou None si non trouvé
        """
        # Requête pour récupérer un patient par sa référence
        return db.query(Patient).filter(Patient.ref_patient == patient_id).first()

    async def create_patient(self, db: Session, patient: CreatePatient):
        """
        Crée un nouveau patient dans la base de données

        Args:
            db (Session): Session de base de données
            patient (CreatePatient): Données du patient à créer

        Returns:
            Patient: Le patient créé
        """
        # Création d'une nouvelle instance de Patient
        patient = Patient(
            ref_patient=patient.id_patient,
            full_name=patient.full_name,
        )

        # Ajout et sauvegarde dans la base de données
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
        """
        Crée une nouvelle réservation dans la base de données

        Args:
            db (Session): Session de base de données
            chambre (Chambre): Chambre à réserver
            patient (Patient): Patient pour qui réserver
            reservation (CreateReservation): Données de la réservation

        Returns:
            Reservation: La réservation créée
        """
        # Création d'une nouvelle instance de Reservation
        reservation = Reservation(
            patient=patient,
            chambre=chambre,
            entree_prevue=reservation.entree_prevue,
            sortie_prevue=reservation.sortie_prevue,
        )

        # Ajout et sauvegarde dans la base de données
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    async def get_reservation_by_id(self, db: Session, reservation_id: int):
        """
        Récupère une réservation par son ID

        Args:
            db (Session): Session de base de données
            reservation_id (int): ID de la réservation à récupérer

        Returns:
            Reservation: La réservation trouvée ou None si non trouvée
        """
        # Requête pour récupérer une réservation par son ID
        return (
            db.query(Reservation)
            .filter(Reservation.id_reservation == reservation_id)
            .first()
        )

    async def cancel_reservation(self, db: Session, reservation_id: int):
        """
        Annule une réservation

        Args:
            db (Session): Session de base de données
            reservation_id (int): ID de la réservation à annuler

        Returns:
            Reservation: La réservation annulée

        Raises:
            HTTPException: Si la réservation n'est pas trouvée
        """
        # Recherche de la réservation dans la base de données
        reservation = (
            db.query(Reservation)
            .filter(Reservation.id_reservation == reservation_id)
            .first()
        )
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="reservation_not_found",
            )

        # Suppression de la réservation
        db.delete(reservation)
        db.commit()
        return reservation

    async def get_reservations(self, db: Session, patient_id: int):
        """
        Récupère les réservations d'un patient

        Args:
            db (Session): Session de base de données
            patient_id (int): ID du patient dont on veut les réservations

        Returns:
            List[Reservation]: Liste des réservations trouvées
        """
        # Requête pour récupérer toutes les réservations d'un patient
        return db.query(Reservation).filter(Reservation.patient_id == patient_id).all()

    async def delete_patient(self, db: Session, patient_id: int):
        """
        Supprime un patient

        Args:
            db (Session): Session de base de données
            patient_id (int): ID du patient à supprimer

        Raises:
            HTTPException: Si le patient n'est pas trouvé
        """
        # Recherche du patient dans la base de données
        patient = db.query(Patient).filter(Patient.id_patient == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="patient_not_found"
            )

        # Suppression du patient
        db.delete(patient)
        db.commit()
