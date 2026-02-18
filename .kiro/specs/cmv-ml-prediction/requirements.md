# Requirements Document

## Introduction

Ce document définit les exigences pour le microservice `cmv_ml`, un service de prédiction de durée d'hospitalisation basé sur un modèle XGBoost pré-entraîné. Ce service s'intègre dans l'architecture microservices existante (Gateway, Patients, Chambres) et permet aux hôtes d'accueil d'obtenir une estimation de la durée de séjour d'un patient à partir de ses antécédents médicaux, tout en respectant les contraintes RGPD.

## Glossary

- **ML_Service**: Le microservice `cmv_ml` responsable des prédictions de durée d'hospitalisation
- **Prediction_Engine**: Le composant qui charge et exécute le modèle XGBoost pour générer les prédictions
- **Feature_Validator**: Le composant qui valide les données d'entrée avant la prédiction
- **Prediction_Store**: Le composant de persistance des métadonnées de prédictions validées
- **SHAP_Explainer**: Le composant optionnel qui calcule l'explicabilité des prédictions via SHAP
- **Gateway**: Le service API Gateway existant qui gère l'authentification JWT
- **User**: Un utilisateur authentifié du système (hôte d'accueil)
- **Features**: Les 22 variables d'entrée du modèle ML (données médicales du patient)
- **Prediction_Metadata**: Les données conservées après validation (prédiction, date, user_id) - sans features médicales

## Requirements

### Requirement 1: Prédiction de durée d'hospitalisation

**User Story:** As a hôte d'accueil, I want to submit patient medical data and receive a predicted length of stay, so that I can better plan hospital resources.

#### Acceptance Criteria

1. WHEN the User submits valid Features via POST /predict, THE Prediction_Engine SHALL return a predicted length of stay in days as a positive number
2. WHEN the User submits Features, THE Feature_Validator SHALL validate that all 22 required fields are present
3. WHEN the User submits Features, THE Feature_Validator SHALL validate that binary fields (gender, comorbidities) contain only 0 or 1
4. WHEN the User submits Features, THE Feature_Validator SHALL validate that continuous fields (hematocrit, neutrophils, sodium, glucose, bloodureanitro, creatinine, bmi, pulse, respiration) are positive numbers
5. IF the User submits invalid Features, THEN THE ML_Service SHALL return a 422 error with descriptive validation messages
6. WHEN a prediction is generated, THE ML_Service SHALL NOT persist the Features to any storage

### Requirement 2: Authentification et autorisation

**User Story:** As a system administrator, I want all ML service endpoints to be protected by JWT authentication, so that only authorized users can access predictions.

#### Acceptance Criteria

1. WHEN a request is received without a valid JWT token, THE ML_Service SHALL return a 401 Unauthorized error
2. WHEN a request is received with an expired JWT token, THE ML_Service SHALL return a 403 Forbidden error
3. WHEN a request is received with a valid JWT token, THE ML_Service SHALL extract the user_id from the token payload
4. THE ML_Service SHALL use the same SECRET_KEY and ALGORITHM as the Gateway for JWT validation

### Requirement 3: Validation des prédictions

**User Story:** As a hôte d'accueil, I want to validate a prediction after manual review, so that the validated prediction is recorded for audit purposes.

#### Acceptance Criteria

1. WHEN a prediction is generated, THE ML_Service SHALL return a unique prediction_id
2. WHEN the User calls POST /predictions/{id}/validate, THE Prediction_Store SHALL persist the Prediction_Metadata
3. WHEN persisting Prediction_Metadata, THE Prediction_Store SHALL store only: prediction_id, predicted_value, validation_date, user_id
4. WHEN persisting Prediction_Metadata, THE Prediction_Store SHALL NOT store any Features (RGPD compliance)
5. IF the User attempts to validate a non-existent prediction_id, THEN THE ML_Service SHALL return a 404 error

### Requirement 4: Historique des prédictions validées

**User Story:** As a system administrator, I want to retrieve the history of validated predictions, so that I can audit system usage.

#### Acceptance Criteria

1. WHEN the User calls GET /predictions, THE ML_Service SHALL return a paginated list of validated Prediction_Metadata
2. WHEN returning Prediction_Metadata, THE ML_Service SHALL include: prediction_id, predicted_value, validation_date, user_id
3. WHEN the User specifies pagination parameters, THE ML_Service SHALL respect limit and offset values

### Requirement 5: Explicabilité SHAP (optionnel)

**User Story:** As a hôte d'accueil, I want to understand which features influenced the prediction, so that I can explain the result to medical staff.

#### Acceptance Criteria

1. WHERE SHAP is enabled, WHEN the User requests a prediction with explain=true, THE SHAP_Explainer SHALL return feature importance values
2. WHERE SHAP is enabled, THE SHAP_Explainer SHALL return a dictionary mapping each feature name to its SHAP contribution value
3. WHERE SHAP is disabled, WHEN the User requests explain=true, THE ML_Service SHALL return the prediction without SHAP values

### Requirement 6: Chargement du modèle

**User Story:** As a system administrator, I want the ML model to be loaded at service startup, so that predictions are fast and the model is validated early.

#### Acceptance Criteria

1. WHEN the ML_Service starts, THE Prediction_Engine SHALL load the XGBoost model from the configured file path
2. IF the model file is missing or corrupted, THEN THE ML_Service SHALL fail to start with a clear error message
3. THE Prediction_Engine SHALL support both .json (native XGBoost) and .joblib model formats

### Requirement 7: Intégration Docker Compose

**User Story:** As a DevOps engineer, I want the ML service to be integrated into the existing Docker Compose setup, so that it can be deployed alongside other services.

#### Acceptance Criteria

1. THE ML_Service SHALL be deployable as a Docker container in the existing cmv network
2. THE ML_Service SHALL expose port 8004 for API access
3. THE ML_Service SHALL connect to its own PostgreSQL database for Prediction_Metadata storage
4. THE ML_Service SHALL share the same SECRET_KEY and ALGORITHM environment variables as other services

### Requirement 8: Conformité RGPD

**User Story:** As a data protection officer, I want to ensure medical data is never persisted, so that the system complies with RGPD regulations.

#### Acceptance Criteria

1. THE ML_Service SHALL process Features only in memory during prediction
2. THE Prediction_Store SHALL NOT contain any columns for medical Features
3. WHEN logging requests, THE ML_Service SHALL NOT log any Features content
4. THE ML_Service SHALL display a RGPD reminder in the API documentation for the /predict endpoint
