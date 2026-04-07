# Requirements Document

## Introduction

The cmv_ml prediction service uses an XGBoost model trained on a clean hospital dataset with no missing values. When the frontend sends `None` for continuous features, the prediction engine currently substitutes `np.nan`, which leads to unreliable predictions because XGBoost's default missing-value handling was never calibrated during training.

This feature introduces mean imputation for missing continuous features: before inference, any `None` continuous feature is replaced with its training-set mean. The prediction response is enriched with metadata indicating which features were imputed, so the frontend and end-users have full transparency.

## Glossary

- **Prediction_Engine**: The `XGBoostPredictionEngine` class in `cmv_ml/app/services/prediction_engine.py` responsible for loading the XGBoost model and executing predictions.
- **Imputation_Service**: A new component responsible for detecting missing continuous features and replacing them with training-set mean values before prediction.
- **Continuous_Feature**: One of the following numeric features that can be `None` in the input: `hematocrit`, `neutrophils`, `sodium`, `glucose`, `bloodureanitro`, `creatinine`, `bmi`, `pulse`, `respiration`, `secondarydiagnosisnonicd9`.
- **Training_Mean**: The arithmetic mean of a Continuous_Feature computed from the training dataset used to build the XGBoost model.
- **Mean_Config_File**: A JSON file co-located with the model file that stores the Training_Mean for each Continuous_Feature.
- **Prediction_Response**: The `PredictionResponse` Pydantic schema returned by the `/predictions/predict` endpoint.
- **Features_Schema**: The `PredictionFeatures` Pydantic schema in `cmv_ml/app/schemas/features.py` that validates incoming prediction requests.

## Requirements

### Requirement 1: Training-Set Mean Configuration

**User Story:** As a data engineer, I want the training-set mean values for continuous features stored in a dedicated JSON configuration file, so that imputation values are maintainable and versioned alongside the model.

#### Acceptance Criteria

1. THE Mean_Config_File SHALL store a JSON object mapping each Continuous_Feature name to its Training_Mean value.
2. THE Mean_Config_File SHALL contain an entry for each of the 10 Continuous_Features: `hematocrit`, `neutrophils`, `sodium`, `glucose`, `bloodureanitro`, `creatinine`, `bmi`, `pulse`, `respiration`, `secondarydiagnosisnonicd9`.
3. WHEN the Prediction_Engine loads the model at application startup, THE Prediction_Engine SHALL also load the Mean_Config_File from the same directory as the model file.
4. IF the Mean_Config_File is missing or unreadable, THEN THE Prediction_Engine SHALL raise a clear error and prevent the application from starting.
5. IF the Mean_Config_File is missing an entry for any Continuous_Feature, THEN THE Prediction_Engine SHALL raise a validation error at startup listing the missing features.

### Requirement 2: Mean Imputation of Missing Continuous Features

**User Story:** As a data scientist, I want missing continuous features replaced with their training-set means before prediction, so that the XGBoost model receives complete input vectors consistent with its training data.

#### Acceptance Criteria

1. WHEN a prediction request contains a `None` value for a Continuous_Feature, THE Imputation_Service SHALL replace that `None` value with the corresponding Training_Mean.
2. WHEN a prediction request provides a non-None value for a Continuous_Feature, THE Imputation_Service SHALL preserve the original value unchanged.
3. THE Imputation_Service SHALL perform imputation before the feature vector is passed to the XGBoost model for inference.
4. THE Imputation_Service SHALL return the list of feature names that were imputed for the current request.
5. FOR ALL valid feature dictionaries, imputing then extracting the feature vector SHALL produce an array with zero `NaN` values (no-NaN invariant).

### Requirement 3: Imputation Transparency in Prediction Response

**User Story:** As a frontend developer, I want the prediction response to indicate which features were imputed, so that I can display appropriate warnings to the clinician.

#### Acceptance Criteria

1. THE Prediction_Response SHALL include an `imputed_features` field containing a dictionary that maps each imputed Continuous_Feature name to the Training_Mean value used.
2. WHEN no features were imputed, THE Prediction_Response SHALL set the `imputed_features` field to an empty dictionary.
3. WHEN one or more features were imputed, THE Prediction_Response SHALL include only the imputed feature names and their substituted mean values in the `imputed_features` field.

### Requirement 4: Feature Schema Compatibility

**User Story:** As a backend developer, I want the existing Pydantic feature schema to remain compatible with the imputation logic, so that current API consumers are not broken.

#### Acceptance Criteria

1. THE Features_Schema SHALL continue to accept `None` as a valid value for each Continuous_Feature.
2. THE Features_Schema SHALL continue to accept valid numeric values for each Continuous_Feature.
3. THE Features_Schema SHALL continue to default binary features (comorbidities, gender, facid_*) to `0`, requiring no imputation for those fields.

### Requirement 5: Imputation Round-Trip Consistency

**User Story:** As a data scientist, I want to verify that imputation produces deterministic and consistent results, so that predictions are reproducible.

#### Acceptance Criteria

1. FOR ALL prediction requests with identical inputs, THE Imputation_Service SHALL produce identical imputed feature vectors (determinism property).
2. FOR ALL prediction requests where every Continuous_Feature is provided (non-None), THE Imputation_Service SHALL return an empty imputed-features list and an unchanged feature vector (identity property).
3. FOR ALL prediction requests where every Continuous_Feature is `None`, THE Imputation_Service SHALL replace each with its Training_Mean and list all 10 Continuous_Features as imputed.
