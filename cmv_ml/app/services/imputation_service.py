"""
Imputation Service for missing continuous features.

Replaces None continuous features with training-set means
before passing the feature vector to the XGBoost model.
"""

import math


class ImputationService:
    """Replaces None continuous features with training-set means."""

    CONTINUOUS_FEATURES: list[str] = [
        "hematocrit",
        "neutrophils",
        "sodium",
        "glucose",
        "bloodureanitro",
        "creatinine",
        "bmi",
        "pulse",
        "respiration",
        "secondarydiagnosisnonicd9",
    ]

    def __init__(self, feature_means: dict[str, float]) -> None:
        """
        Args:
            feature_means: Mapping of continuous feature name -> training mean.

        Raises:
            ValueError: If any of the 10 continuous features is missing
                        or has a non-finite / non-positive value.
        """
        missing = [f for f in self.CONTINUOUS_FEATURES if f not in feature_means]
        invalid = [
            f
            for f in self.CONTINUOUS_FEATURES
            if f in feature_means
            and (
                not isinstance(feature_means[f], (int, float))
                or not math.isfinite(feature_means[f])
                or feature_means[f] <= 0
            )
        ]

        errors: list[str] = []
        if missing:
            errors.append(f"Missing keys: {missing}")
        if invalid:
            errors.append(f"Invalid values for keys: {invalid}")
        if errors:
            raise ValueError("; ".join(errors))

        self._feature_means: dict[str, float] = {
            f: float(feature_means[f]) for f in self.CONTINUOUS_FEATURES
        }

    @property
    def feature_means(self) -> dict[str, float]:
        """Read-only access to the stored training means."""
        return dict(self._feature_means)

    def impute(self, features: dict) -> tuple[dict, dict[str, float]]:
        """
        Replace None values with training means.

        Args:
            features: Raw feature dict from PredictionFeatures.model_dump().

        Returns:
            (clean_features, imputed_features)
            - clean_features: Copy of features with Nones replaced.
            - imputed_features: {feature_name: mean_value_used} for imputed fields only.
        """
        clean_features = dict(features)
        imputed_features: dict[str, float] = {}

        for feature_name in self.CONTINUOUS_FEATURES:
            if feature_name in clean_features and clean_features[feature_name] is None:
                mean_value = self._feature_means[feature_name]
                clean_features[feature_name] = mean_value
                imputed_features[feature_name] = mean_value

        return clean_features, imputed_features
