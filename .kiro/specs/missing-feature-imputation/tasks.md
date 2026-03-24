# Implementation Plan: Missing Feature Imputation

## Overview

Implement mean imputation for missing continuous features in the cmv_ml prediction service. The work proceeds bottom-up: data file → service class → engine integration → schema update → router wiring → tests.

## Tasks

- [x] 1. Create the feature means configuration file and ImputationService
  - [x] 1.1 Create `cmv_ml/models/feature_means.json` with training-set means for the 10 continuous features
    - JSON object mapping each continuous feature name to its training mean value
    - Keys: `hematocrit`, `neutrophils`, `sodium`, `glucose`, `bloodureanitro`, `creatinine`, `bmi`, `pulse`, `respiration`, `secondarydiagnosisnonicd9`
    - Values: representative positive floats (use illustrative values from design until real training means are provided)
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Create `cmv_ml/app/services/imputation_service.py` with the `ImputationService` class
    - Define `CONTINUOUS_FEATURES` class-level list of the 10 feature names
    - `__init__(self, feature_means: dict[str, float])`: validate all 10 keys present and values are finite positive floats; raise `ValueError` listing missing/invalid keys
    - `impute(self, features: dict) -> tuple[dict, dict[str, float]]`: return `(clean_features, imputed_features)` where `None` continuous values are replaced with their training mean
    - _Requirements: 1.5, 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.3_

  - [ ]* 1.3 Write property test: Imputation correctness (Property 1)
    - **Property 1: Imputation correctness**
    - **Validates: Requirements 2.1, 2.2, 2.4, 3.1, 3.3, 5.2**
    - File: `cmv_ml/app/tests/test_imputation_properties.py`
    - Use Hypothesis to generate dicts of 10 continuous features where each is independently `None` or a positive float
    - Assert: every originally-`None` feature equals its training mean in output; every non-`None` feature is unchanged; `imputed_features` keys match exactly the `None` inputs

  - [ ]* 1.4 Write property test: No-NaN invariant (Property 2)
    - **Property 2: No-NaN invariant**
    - **Validates: Requirements 2.5**
    - File: `cmv_ml/app/tests/test_imputation_properties.py`
    - After imputation, convert to numpy array via `_features_to_array` and assert `np.isnan(arr).sum() == 0`

  - [ ]* 1.5 Write property test: Missing config keys produce validation error (Property 3)
    - **Property 3: Missing config keys produce validation error**
    - **Validates: Requirements 1.5**
    - File: `cmv_ml/app/tests/test_imputation_properties.py`
    - Generate random strict subsets of the 10 feature names; construct `ImputationService` with partial dict; assert `ValueError` and check missing keys in message

  - [ ]* 1.6 Write property test: Schema accepts None and valid numerics (Property 4)
    - **Property 4: Schema accepts None and valid numerics for continuous features**
    - **Validates: Requirements 4.1, 4.2**
    - File: `cmv_ml/app/tests/test_imputation_properties.py`
    - Generate a continuous feature name and a positive float; construct `PredictionFeatures` with that feature set to the float, then to `None`; both should succeed

- [x] 2. Integrate imputation into the prediction engine and startup
  - [x] 2.1 Add `load_feature_means(path: str)` method to `XGBoostPredictionEngine` in `cmv_ml/app/services/prediction_engine.py`
    - Read and parse `feature_means.json`; raise `FileNotFoundError` if missing, `json.JSONDecodeError` if invalid
    - Instantiate `ImputationService` with the loaded means dict (validation happens in `ImputationService.__init__`)
    - Expose `imputation_service` property and `feature_means` property (read-only)
    - _Requirements: 1.3, 1.4, 1.5_

  - [x] 2.2 Update `lifespan` in `cmv_ml/app/main.py` to call `load_feature_means` after `load_model`
    - Compute means path: `os.path.join(os.path.dirname(MODEL_PATH), "feature_means.json")`
    - Wrap in try/except; raise `RuntimeError` on failure to prevent app startup
    - _Requirements: 1.3, 1.4_

  - [ ]* 2.3 Write unit tests for engine mean-loading in `cmv_ml/app/tests/test_imputation_unit.py`
    - `test_load_feature_means_success`: load valid JSON, verify engine exposes means dict
    - `test_load_feature_means_file_not_found`: non-existent path → `FileNotFoundError`
    - `test_load_feature_means_invalid_json`: broken JSON → error
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update response schema and router to wire imputation into the prediction flow
  - [x] 4.1 Add `imputed_features` field to `PredictionResponse` in `cmv_ml/app/schemas/predictions.py`
    - `imputed_features: dict[str, float] = Field(default_factory=dict, description="Map of imputed feature names to the training-mean value used.")`
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 4.2 Update the `predict` endpoint in `cmv_ml/app/routers/predictions.py`
    - After `features.model_dump()`, call `prediction_engine.imputation_service.impute(features_dict)` to get `(clean_features, imputed_features)`
    - Pass `clean_features` to `prediction_engine.predict()`
    - Include `imputed_features` in the `PredictionResponse` constructor
    - _Requirements: 2.3, 3.1, 3.2, 3.3_

  - [ ]* 4.3 Write unit tests for imputation edge cases in `cmv_ml/app/tests/test_imputation_unit.py`
    - `test_impute_all_none`: all 10 continuous features `None` → all replaced, all 10 listed as imputed
    - `test_impute_none_missing`: all features provided → empty imputed dict, values unchanged
    - `test_response_schema_has_imputed_features`: `PredictionResponse` accepts `imputed_features` dict and defaults to `{}`
    - `test_binary_features_default_to_zero`: `PredictionFeatures()` with no binary args → all binary fields are 0
    - _Requirements: 3.2, 4.3, 5.2, 5.3_

- [x] 5. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis with `@settings(max_examples=100)` minimum
- The implementation language is Python (matching the existing codebase and design)
- All test files go in `cmv_ml/app/tests/`
