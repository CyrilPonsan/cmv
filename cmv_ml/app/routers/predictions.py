"""
Router pour les endpoints de prédiction de durée d'hospitalisation.

RGPD: Les données médicales (features) ne sont JAMAIS persistées.
Seules les métadonnées de prédiction validées sont stockées.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..dependancies.auth import check_authorization
from ..dependancies.db_session import get_db
from ..repositories.predictions_crud import predictions_repository
from ..schemas.features import PredictionFeatures
from ..schemas.predictions import (
    PaginatedPredictions,
    PredictionResponse,
    ValidatedPredictionSchema,
)
from ..services.prediction_cache import prediction_cache
from ..services.prediction_engine import (
    ModelNotLoadedError,
    XGBoostPredictionEngine,
)
from ..services.shap_explainer import (
    XGBoostShapExplainer,
    ShapDisabledError,
    create_shap_explainer,
)
from ..utils.config import SHAP_ENABLED

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Instance du moteur de prédiction (sera initialisée au démarrage de l'app)
prediction_engine = XGBoostPredictionEngine()

# Instance du SHAP explainer (sera initialisée après le chargement du modèle)
shap_explainer: XGBoostShapExplainer | None = None


def initialize_shap_explainer() -> None:
    """
    Initialize the SHAP explainer after the model is loaded.

    Should be called after prediction_engine.load_model() in the app lifespan.
    """
    global shap_explainer

    if not prediction_engine.is_loaded:
        return

    if SHAP_ENABLED:
        shap_explainer = create_shap_explainer(
            model=prediction_engine._model,
            feature_order=prediction_engine.get_feature_order(),
        )


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    features: PredictionFeatures,
    explain: bool = Query(
        False, description="Inclure les valeurs SHAP pour l'explicabilité"
    ),
    current_user: dict = Depends(check_authorization),
) -> PredictionResponse:
    """
    Prédit la durée d'hospitalisation à partir des features médicales.

    ⚠️ **RGPD**: Les données médicales (features) ne sont PAS stockées.
    Elles sont traitées uniquement en mémoire pendant la prédiction.

    Args:
        features: Les 22 features médicales du patient
        explain: Si True, inclut les valeurs SHAP (si disponible)
        current_user: Utilisateur authentifié (injecté via JWT)

    Returns:
        PredictionResponse contenant:
        - prediction_id: UUID unique pour validation ultérieure
        - predicted_length_of_stay: Durée prédite en jours
        - shap_values: Contributions SHAP par feature (optionnel)

    Raises:
        HTTPException 503: Si le modèle n'est pas chargé
        HTTPException 500: Si une erreur survient pendant la prédiction
    """
    # Vérifier que le modèle est chargé
    if not prediction_engine.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )

    try:
        # Convertir les features en dictionnaire
        features_dict = features.model_dump()

        print(
            f"Received prediction request from user {current_user.get('id_user')}: {features_dict}"
        )

        # Exécuter la prédiction
        predicted_value = prediction_engine.predict(features_dict)

        # Générer un ID unique pour cette prédiction
        prediction_id = uuid4()

        # Stocker dans le cache pour validation ultérieure
        # prediction_cache.store(prediction_id, predicted_value)

        # Préparer les valeurs SHAP si demandées
        shap_values = None
        if explain and SHAP_ENABLED and shap_explainer is not None:
            try:
                shap_values = shap_explainer.explain(features_dict)
            except ShapDisabledError:
                # SHAP is disabled, return prediction without SHAP values
                shap_values = None
            except Exception:
                # SHAP calculation failed, return prediction without SHAP values
                shap_values = None

        return PredictionResponse(
            prediction_id=prediction_id,
            predicted_length_of_stay=predicted_value,
            shap_values=shap_values,
        )

    except ModelNotLoadedError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )
    except Exception as e:
        import logging

        logging.exception(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post("/{prediction_id}/validate")
async def validate_prediction(
    prediction_id: UUID,
    current_user: dict = Depends(check_authorization),
    db: Session = Depends(get_db),
) -> dict:
    """
    Valide une prédiction pour l'enregistrer dans l'historique.

    La prédiction doit avoir été générée précédemment via POST /predict
    et ne pas avoir expiré du cache (TTL: 30 minutes).

    Args:
        prediction_id: UUID de la prédiction à valider
        current_user: Utilisateur authentifié (injecté via JWT)
        db: Session de base de données

    Returns:
        dict avec message de confirmation et détails de la prédiction validée

    Raises:
        HTTPException 404: Si la prédiction n'existe pas ou a expiré
        HTTPException 409: Si la prédiction a déjà été validée
    """
    # Vérifier si la prédiction existe déjà en base (déjà validée)
    if predictions_repository.exists(db, prediction_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prediction already validated",
        )

    # Récupérer la prédiction du cache
    predicted_value = prediction_cache.get(prediction_id)

    if predicted_value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    # Extraire le user_id du token
    # user_id = current_user.get("user_id")
    user_id = current_user.get("id_user")

    # Persister la prédiction validée
    validation_date = datetime.now(timezone.utc)
    predictions_repository.save_validated(
        db=db,
        prediction_id=prediction_id,
        predicted_value=predicted_value,
        user_id=user_id,
        validation_date=validation_date,
    )

    # Supprimer du cache après validation
    prediction_cache.remove(prediction_id)

    return {
        "message": "Prediction validated successfully",
        "prediction_id": str(prediction_id),
        "predicted_value": predicted_value,
        "validation_date": validation_date.isoformat(),
    }


@router.get("/", response_model=PaginatedPredictions)
async def get_predictions(
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats par page"),
    offset: int = Query(0, ge=0, description="Nombre de résultats à ignorer"),
    current_user: dict = Depends(check_authorization),
    db: Session = Depends(get_db),
) -> PaginatedPredictions:
    """
    Récupère l'historique des prédictions validées avec pagination.

    Args:
        limit: Nombre maximum de résultats (1-100, défaut: 20)
        offset: Position de départ pour la pagination (défaut: 0)
        current_user: Utilisateur authentifié (injecté via JWT)
        db: Session de base de données

    Returns:
        PaginatedPredictions contenant:
        - items: Liste des prédictions validées
        - total: Nombre total de prédictions
        - limit: Limite utilisée
        - offset: Offset utilisé
    """
    # Récupérer les prédictions avec pagination
    predictions = predictions_repository.get_all(db, limit=limit, offset=offset)

    # Compter le total pour la pagination
    total = predictions_repository.count(db)

    # Convertir en schemas
    items = [
        ValidatedPredictionSchema(
            id=p.id,
            predicted_value=p.predicted_value,
            validation_date=p.validation_date,
            user_id=p.user_id,
        )
        for p in predictions
    ]

    return PaginatedPredictions(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
