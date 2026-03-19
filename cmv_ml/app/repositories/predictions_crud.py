"""
Repository pour la gestion des prédictions validées.

RGPD: Ce repository ne stocke que les métadonnées de prédiction.
Les features médicales ne sont JAMAIS persistées.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from this import d
from typing import Protocol
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..schemas.features import PredictionFeatures
from ..sql.models import Prediction


class PredictionRepositoryProtocol(Protocol):
    """Interface du repository de prédictions."""

    def create_prediction(
        self,
        db: Session,
        features: PredictionFeatures,
    ) -> dict:
        """Crée une prédiction dans la base de données."""
        ...


class PredictionCrud(ABC):
    """Interface abstraite définissant les méthodes CRUD pour les prédictions."""

    @abstractmethod
    def create_prediction(
        self,
        db: Session,
        features: PredictionFeatures,
    ) -> dict:
        """Persiste une prédiction avec ses features."""
        pass


class PgPredictionsRepository(PredictionCrud):
    """
    Implémentation PostgreSQL du repository de prédictions.

    """

    def update_prediction(
        self,
        db: Session,
        adid: str,
    ) -> dict:
        """
        Met à jour une prédiction existante.

        Args:
            db: Session de base de données
            prediction_id: ID de la prédiction à mettre à jour
            features: Nouvelles features de la prédiction

        Returns:
            dict: Message de confirmation
        """
        db_prediction = db.query(Prediction).filter(Prediction.adid == adid).first()
        if not db_prediction:
            return {"message": "Prédiction non trouvée"}
        lenghtofstay = func.now() - db_prediction.vdate
        db_prediction.lenghtofstay = lenghtofstay
        db_prediction.vdate = None
        db_prediction.adid = None
        db.commit()
        db.refresh(db_prediction)
        return {"message": "Mise à jour réussie"}

    def create_prediction(
        self,
        db: Session,
        features: PredictionFeatures,
    ) -> dict:
        """
        Crée une prédiction dans la base de données.

        Args:
            db: Session de base de données
            features: Features de la prédiction

        Returns:
            Prediction: La prédiction créée
        """
        db_prediction = Prediction(**features.model_dump())
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return {"message": "Enregistrement réussi youhou !"}


# Instance singleton du repository pour injection de dépendances
predictions_repository = PgPredictionsRepository()
