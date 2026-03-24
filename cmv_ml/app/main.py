"""
Point d'entrée de l'application CMV ML Prediction Service.

Ce microservice prédit la durée d'hospitalisation d'un patient à partir
de 22 features médicales, en utilisant un modèle XGBoost pré-entraîné.

RGPD: Les données médicales ne sont JAMAIS persistées.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers.predictions import (
    prediction_engine,
    router as predictions_router,
    initialize_shap_explainer,
)
from .services.prediction_engine import ModelNotLoadedError
from .utils.config import MODEL_PATH, SHAP_ENABLED
from .sql import models
from .utils.database import engine

print(f"MODEL PATH {MODEL_PATH}")


# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)


class PredictionError(Exception):
    """Erreur lors de l'inférence du modèle."""

    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.

    Startup: Charge le modèle XGBoost depuis le chemin configuré.
    Shutdown: Cleanup si nécessaire.
    """
    # Startup: charger le modèle
    try:
        prediction_engine.load_model(MODEL_PATH)
    except FileNotFoundError:
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")

    # Load feature means for imputation
    try:
        means_path = os.path.join(os.path.dirname(MODEL_PATH), "feature_means.json")
        prediction_engine.load_feature_means(means_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load feature means: {e}")

    # Initialize SHAP explainer if enabled
    if SHAP_ENABLED:
        try:
            initialize_shap_explainer()
        except Exception as e:
            # SHAP initialization failure is not fatal - log and continue
            import logging

            logging.warning(f"Failed to initialize SHAP explainer: {e}")

    yield

    # Shutdown: cleanup si nécessaire
    pass


app = FastAPI(
    title="CMV ML Prediction Service",
    description=(
        "Service de prédiction de durée d'hospitalisation basé sur XGBoost.\n\n"
        "⚠️ **RGPD**: Les données médicales (features) ne sont JAMAIS stockées. "
        "Elles sont traitées uniquement en mémoire pendant la prédiction."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gestionnaires d'erreurs
@app.exception_handler(PredictionError)
async def prediction_error_handler(request, exc):
    """Gère les erreurs de prédiction."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Prediction failed"},
    )


@app.exception_handler(ModelNotLoadedError)
async def model_not_loaded_handler(request, exc):
    """Gère les erreurs de modèle non chargé."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Service unavailable"},
    )


# Inclusion des routers
app.include_router(predictions_router)


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé du service."""
    return {
        "status": "healthy",
        "model_loaded": prediction_engine.is_loaded,
    }
