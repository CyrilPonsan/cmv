"""
SHAP Explainer for XGBoost model predictions.

This module provides explainability for predictions using SHAP
(SHapley Additive exPlanations) values.
"""

from typing import Protocol
import numpy as np

from cmv_ml.app.utils.config import SHAP_ENABLED


class ShapExplainerProtocol(Protocol):
    """Interface de l'explicateur SHAP."""
    
    def explain(self, features: dict) -> dict[str, float]:
        """Retourne les contributions SHAP par feature."""
        ...


class ShapDisabledError(Exception):
    """Exception raised when SHAP is disabled but explanation is requested."""
    pass


class XGBoostShapExplainer:
    """Implémentation SHAP pour XGBoost."""
    
    def __init__(self, model, feature_order: list[str]):
        """
        Initialize the SHAP explainer.
        
        Args:
            model: The XGBoost model (Booster or sklearn-style)
            feature_order: List of feature names in the order expected by the model
        """
        self._explainer = None
        self._model = model
        self._feature_order = feature_order
        self._initialized = False
    
    def _initialize_explainer(self) -> None:
        """Lazily initialize the SHAP explainer."""
        if self._initialized:
            return
        
        if not SHAP_ENABLED:
            raise ShapDisabledError("SHAP is disabled in configuration")
        
        import shap
        
        # Create TreeExplainer for XGBoost model
        self._explainer = shap.TreeExplainer(self._model)
        self._initialized = True
    
    def explain(self, features: dict) -> dict[str, float]:
        """
        Calcule les valeurs SHAP pour une prédiction.
        
        Args:
            features: Dictionnaire des 22 features médicales
            
        Returns:
            Dictionnaire mappant chaque nom de feature à sa contribution SHAP
            
        Raises:
            ShapDisabledError: Si SHAP est désactivé dans la configuration
        """
        if not SHAP_ENABLED:
            raise ShapDisabledError("SHAP is disabled in configuration")
        
        # Initialize explainer on first use
        self._initialize_explainer()
        
        # Convert features to numpy array in correct order
        feature_array = self._features_to_array(features)
        
        # Calculate SHAP values
        shap_values = self._explainer.shap_values(feature_array)
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # Multi-class output - take first class for regression
            values = shap_values[0][0]
        elif len(shap_values.shape) == 2:
            # Single output - shape (1, n_features)
            values = shap_values[0]
        else:
            values = shap_values
        
        # Map SHAP values to feature names
        return {
            name: float(values[i])
            for i, name in enumerate(self._feature_order)
        }
    
    def _features_to_array(self, features: dict) -> np.ndarray:
        """Convert features dictionary to numpy array in correct order."""
        values = [features[name] for name in self._feature_order]
        return np.array([values], dtype=np.float32)
    
    @property
    def is_enabled(self) -> bool:
        """Check if SHAP is enabled in configuration."""
        return SHAP_ENABLED


def create_shap_explainer(model, feature_order: list[str]) -> XGBoostShapExplainer | None:
    """
    Factory function to create a SHAP explainer if enabled.
    
    Args:
        model: The XGBoost model
        feature_order: List of feature names
        
    Returns:
        XGBoostShapExplainer instance if SHAP is enabled, None otherwise
    """
    if not SHAP_ENABLED:
        return None
    
    return XGBoostShapExplainer(model, feature_order)
