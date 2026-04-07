"""Schemas de réponse pour les endpoints de prédiction."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """
    Réponse de l'endpoint /predict.
    
    Contient l'identifiant unique de la prédiction, la durée d'hospitalisation
    prédite, et optionnellement les valeurs SHAP pour l'explicabilité.
    """

    prediction_id: UUID
    predicted_length_of_stay: float
    shap_values: dict[str, float] | None = None
    imputed_features: dict[str, float] = Field(default_factory=dict, description="Map of imputed feature names to the training-mean value used.")


class ValidatedPredictionSchema(BaseModel):
    """
    Schema d'une prédiction validée.
    
    Représente les métadonnées d'une prédiction après validation par l'utilisateur.
    Conforme RGPD: ne contient aucune donnée médicale (features).
    """

    id: UUID
    predicted_value: float
    validation_date: datetime
    user_id: int


class PaginatedPredictions(BaseModel):
    """
    Réponse paginée des prédictions validées.
    
    Utilisée par l'endpoint GET /predictions pour retourner l'historique
    des prédictions avec support de pagination.
    """

    items: list[ValidatedPredictionSchema]
    total: int
    limit: int
    offset: int
