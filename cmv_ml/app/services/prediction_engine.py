"""
Prediction Engine for XGBoost model.

This module handles loading and executing the XGBoost model for
hospital length of stay predictions.
"""

from typing import Protocol
import json
import numpy as np

from app.services.imputation_service import ImputationService


class PredictionEngineProtocol(Protocol):
    """Interface du moteur de prédiction."""
    
    def load_model(self, path: str) -> None:
        """Charge le modèle depuis un fichier."""
        ...
    
    def predict(self, features: dict) -> float:
        """Retourne la prédiction de durée d'hospitalisation."""
        ...
    
    def get_feature_order(self) -> list[str]:
        """Retourne l'ordre des features attendu par le modèle."""
        ...


class ModelNotLoadedError(Exception):
    """Exception raised when the model is not loaded."""
    pass


class ModelLoadError(Exception):
    """Exception raised when the model fails to load."""
    pass


class XGBoostPredictionEngine:
    """Implémentation avec XGBoost."""
    
    def __init__(self):
        self._model = None
        self._imputation_service: ImputationService | None = None
        self._feature_means: dict[str, float] | None = None
        # Ordre des features tel qu'attendu par le modèle XGBoost
        self._feature_order = [
            "rcount", "gender", "dialysisrenalendstage", "asthma", "irondef", 
            "pneum", "substancedependence", "psychologicaldisordermajor", 
            "depress", "psychother", "fibrosisandother", "malnutrition", "hemo",
            "hematocrit", "neutrophils", "sodium", "glucose", "bloodureanitro",
            "creatinine", "bmi", "pulse", "respiration", "secondarydiagnosisnonicd9",
            "facid_B", "facid_C", "facid_D", "facid_E"
        ]
    
    def load_model(self, path: str) -> None:
        """
        Charge le modèle XGBoost (.json ou .joblib).
        
        Args:
            path: Chemin vers le fichier du modèle
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ModelLoadError: Si le modèle ne peut pas être chargé
        """
        import os
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        try:
            if path.endswith('.json'):
                self._load_json_model(path)
            elif path.endswith('.joblib'):
                self._load_joblib_model(path)
            else:
                # Try to detect format by attempting both loaders
                try:
                    self._load_json_model(path)
                except Exception:
                    self._load_joblib_model(path)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ModelLoadError(f"Failed to load model from {path}: {e}")
    
    def _load_json_model(self, path: str) -> None:
        """Load model from native XGBoost JSON format."""
        import xgboost as xgb
        
        self._model = xgb.Booster()
        self._model.load_model(path)
    
    def _load_joblib_model(self, path: str) -> None:
        """Load model from joblib format."""
        import joblib
        
        self._model = joblib.load(path)
    
    def predict(self, features: dict) -> float:
        """
        Exécute la prédiction.
        
        Args:
            features: Dictionnaire des 22 features médicales
            
        Returns:
            Prédiction de durée d'hospitalisation en jours (float positif)
            
        Raises:
            ModelNotLoadedError: Si le modèle n'est pas chargé
        """
        if self._model is None:
            raise ModelNotLoadedError("Model not loaded. Call load_model() first.")
        
        # Convert features dict to numpy array in correct order
        feature_array = self._features_to_array(features)
        
        # Execute prediction based on model type
        return self._execute_prediction(feature_array)
    
    def _features_to_array(self, features: dict) -> np.ndarray:
        """Convert features dictionary to numpy array in correct order, replacing None with np.nan."""
        values = [features[name] if features[name] is not None else np.nan for name in self._feature_order]
        return np.array([values], dtype=np.float32)
    
    def _execute_prediction(self, feature_array: np.ndarray) -> float:
        """Execute prediction based on model type."""
        import xgboost as xgb
        
        # Check if model is a Booster (native XGBoost) or sklearn-style
        if isinstance(self._model, xgb.Booster):
            dmatrix = xgb.DMatrix(feature_array, feature_names=self._feature_order)
            prediction = self._model.predict(dmatrix)
        else:
            # sklearn-style model (from joblib)
            prediction = self._model.predict(feature_array)
        
        # Return single prediction value
        result = float(prediction[0])
        
        # Ensure positive value (length of stay cannot be negative)
        return max(result, 0.0)
    
    def get_feature_order(self) -> list[str]:
        """Retourne l'ordre des features attendu par le modèle."""
        return self._feature_order.copy()
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None

    def load_feature_means(self, path: str) -> None:
        """
        Load feature means from a JSON file and instantiate the ImputationService.

        Args:
            path: Path to the feature_means.json file.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            ValueError: If required keys are missing or values are invalid
                        (raised by ImputationService.__init__).
        """
        with open(path, "r") as f:
            means = json.load(f)

        self._imputation_service = ImputationService(means)
        self._feature_means = self._imputation_service.feature_means

    @property
    def imputation_service(self) -> ImputationService | None:
        """Read-only access to the ImputationService instance."""
        return self._imputation_service

    @property
    def feature_means(self) -> dict[str, float] | None:
        """Read-only access to the loaded feature means dict."""
        return dict(self._feature_means) if self._feature_means is not None else None
