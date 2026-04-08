"""
Repository pour la gestion des prédictions validées.

RGPD: Ce repository ne stocke que les métadonnées de prédiction.
Les features médicales ne sont JAMAIS persistées.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..sql.models import ValidatedPrediction


class PredictionRepositoryProtocol(Protocol):
    """Interface du repository de prédictions."""
    
    def save_validated(
        self, 
        db: Session,
        prediction_id: UUID, 
        predicted_value: float, 
        user_id: int,
        validation_date: datetime
    ) -> ValidatedPrediction:
        """Persiste une prédiction validée (métadonnées uniquement)."""
        ...
    
    def get_all(self, db: Session, limit: int, offset: int) -> list[dict]:
        """Récupère l'historique des prédictions validées."""
        ...
    
    def exists(self, db: Session, prediction_id: UUID) -> bool:
        """Vérifie si une prédiction existe."""
        ...
    
    def count(self, db: Session) -> int:
        """Retourne le nombre total de prédictions validées."""
        ...


class PredictionCrud(ABC):
    """Interface abstraite définissant les méthodes CRUD pour les prédictions."""

    @abstractmethod
    def save_validated(
        self,
        db: Session,
        prediction_id: UUID,
        predicted_value: float,
        user_id: int,
        validation_date: datetime
    ) -> ValidatedPrediction:
        """Persiste une prédiction validée (métadonnées uniquement)."""
        pass

    @abstractmethod
    def get_all(self, db: Session, limit: int, offset: int) -> list[ValidatedPrediction]:
        """Récupère l'historique des prédictions validées avec pagination."""
        pass

    @abstractmethod
    def exists(self, db: Session, prediction_id: UUID) -> bool:
        """Vérifie si une prédiction existe déjà dans la base."""
        pass

    @abstractmethod
    def count(self, db: Session) -> int:
        """Retourne le nombre total de prédictions validées."""
        pass


class PgPredictionsRepository(PredictionCrud):
    """
    Implémentation PostgreSQL du repository de prédictions.
    
    RGPD Compliance: Ce repository stocke uniquement les métadonnées.
    Les features médicales ne sont JAMAIS persistées.
    """

    def save_validated(
        self,
        db: Session,
        prediction_id: UUID,
        predicted_value: float,
        user_id: int,
        validation_date: datetime
    ) -> ValidatedPrediction:
        """
        Persiste une prédiction validée dans la base de données.
        
        Args:
            db: Session de base de données
            prediction_id: UUID unique de la prédiction
            predicted_value: Valeur prédite (durée d'hospitalisation en jours)
            user_id: ID de l'utilisateur qui a validé la prédiction
            validation_date: Date de validation de la prédiction
            
        Returns:
            ValidatedPrediction: La prédiction validée créée
        """
        db_prediction = ValidatedPrediction(
            id=prediction_id,
            predicted_value=predicted_value,
            user_id=user_id,
            validation_date=validation_date,
            created_at=datetime.utcnow()
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction

    def get_all(self, db: Session, limit: int, offset: int) -> list[ValidatedPrediction]:
        """
        Récupère l'historique des prédictions validées avec pagination.
        
        Args:
            db: Session de base de données
            limit: Nombre maximum de résultats à retourner
            offset: Nombre de résultats à ignorer (pour la pagination)
            
        Returns:
            list[ValidatedPrediction]: Liste des prédictions validées
        """
        return (
            db.query(ValidatedPrediction)
            .order_by(ValidatedPrediction.validation_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def exists(self, db: Session, prediction_id: UUID) -> bool:
        """
        Vérifie si une prédiction existe déjà dans la base.
        
        Args:
            db: Session de base de données
            prediction_id: UUID de la prédiction à vérifier
            
        Returns:
            bool: True si la prédiction existe, False sinon
        """
        result = (
            db.query(ValidatedPrediction)
            .filter(ValidatedPrediction.id == prediction_id)
            .first()
        )
        return result is not None

    def count(self, db: Session) -> int:
        """
        Retourne le nombre total de prédictions validées.
        
        Args:
            db: Session de base de données
            
        Returns:
            int: Nombre total de prédictions validées
        """
        return db.query(func.count(ValidatedPrediction.id)).scalar() or 0


# Instance singleton du repository pour injection de dépendances
predictions_repository = PgPredictionsRepository()
