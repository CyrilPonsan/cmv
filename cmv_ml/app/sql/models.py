"""
Modèles SQLAlchemy pour le service ML de prédiction.

RGPD: Ce modèle ne contient PAS de colonnes pour les features médicales.
Seules les métadonnées de prédiction sont stockées.
"""
from datetime import datetime
import uuid

from sqlalchemy import Column, Float, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID

from ..utils.database import Base


class ValidatedPrediction(Base):
    """
    Modèle SQLAlchemy pour les prédictions validées.
    
    RGPD Compliance: Ce modèle stocke uniquement les métadonnées de prédiction.
    Les features médicales ne sont JAMAIS persistées.
    """
    
    __tablename__ = "validated_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    predicted_value = Column(Float, nullable=False)
    validation_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Index supplémentaire pour les requêtes par date de validation
    __table_args__ = (
        Index('idx_predictions_validation_date', 'validation_date'),
    )
