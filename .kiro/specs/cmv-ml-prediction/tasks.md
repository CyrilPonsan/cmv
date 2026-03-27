# Implementation Plan: CMV ML Prediction Service

## Overview

Ce plan implémente le microservice `cmv_ml` pour la prédiction de durée d'hospitalisation. L'implémentation suit la structure des microservices existants (cmv_patients, cmv_chambres) et utilise FastAPI avec XGBoost.

## Tasks

- [x] 1. Initialiser la structure du projet cmv_ml
  - [x] 1.1 Créer la structure de répertoires du microservice
    - Créer `cmv_ml/app/` avec les sous-dossiers : `routers/`, `services/`, `repositories/`, `schemas/`, `sql/`, `utils/`, `dependancies/`, `tests/`
    - Créer les fichiers `__init__.py` dans chaque dossier
    - _Requirements: 7.1_
  
  - [x] 1.2 Créer les fichiers de configuration
    - Créer `cmv_ml/requirements.txt` avec les dépendances (fastapi, uvicorn, sqlalchemy, pydantic, xgboost, joblib, python-jose, passlib, hypothesis, pytest)
    - Créer `cmv_ml/Dockerfile` basé sur le modèle de cmv_patients
    - Créer `cmv_ml/.env` avec les variables d'environnement
    - _Requirements: 7.1, 7.4_
  
  - [x] 1.3 Créer le fichier de configuration de l'application
    - Créer `cmv_ml/app/utils/config.py` avec DATABASE_URL, SECRET_KEY, ALGORITHM, MODEL_PATH, SHAP_ENABLED
    - _Requirements: 2.4, 6.1_

- [x] 2. Implémenter la validation des features
  - [x] 2.1 Créer le schema Pydantic PredictionFeatures
    - Créer `cmv_ml/app/schemas/features.py` avec les 22 champs validés
    - Utiliser `Literal[0, 1]` pour les champs binaires
    - Utiliser `Field(gt=0)` pour les champs continus
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [ ]* 2.2 Écrire le test property-based pour la validation des features
    - **Property 2: Feature Validation Completeness**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**

- [x] 3. Implémenter le moteur de prédiction
  - [x] 3.1 Créer le Prediction Engine
    - Créer `cmv_ml/app/services/prediction_engine.py`
    - Implémenter `load_model()` avec support .json et .joblib
    - Implémenter `predict()` qui convertit les features en array numpy et appelle le modèle
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ]* 3.2 Écrire le test property-based pour la prédiction
    - **Property 1: Prediction Output Validity**
    - **Validates: Requirements 1.1**
  
  - [ ]* 3.3 Écrire le test property-based pour l'unicité des IDs
    - **Property 4: Prediction ID Uniqueness**
    - **Validates: Requirements 3.1**

- [x] 4. Implémenter l'authentification JWT
  - [x] 4.1 Créer le module d'authentification
    - Créer `cmv_ml/app/dependancies/auth.py` basé sur cmv_patients
    - Implémenter `check_authorization()` qui décode le JWT et extrait user_id
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ]* 4.2 Écrire le test property-based pour l'extraction user_id
    - **Property 3: JWT User Extraction**
    - **Validates: Requirements 2.3**

- [x] 5. Checkpoint - Vérifier les composants de base
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implémenter la couche de persistance
  - [x] 6.1 Créer le modèle SQLAlchemy ValidatedPrediction
    - Créer `cmv_ml/app/sql/models.py` avec la table validated_predictions
    - Colonnes : id (UUID), predicted_value (Float), validation_date (DateTime), user_id (Integer)
    - NE PAS inclure de colonnes pour les features médicales (RGPD)
    - _Requirements: 3.3, 3.4, 8.2_
  
  - [x] 6.2 Créer le repository de prédictions
    - Créer `cmv_ml/app/repositories/predictions_crud.py`
    - Implémenter `save_validated()`, `get_all()`, `exists()`, `count()`
    - _Requirements: 3.2, 4.1_
  
  - [x] 6.3 Créer le cache en mémoire pour les prédictions
    - Créer `cmv_ml/app/services/prediction_cache.py`
    - Implémenter `store()`, `get()`, `remove()` avec TTL de 30 minutes
    - _Requirements: 3.1, 3.2_
  
  - [ ]* 6.4 Écrire le test property-based pour le round-trip validation
    - **Property 5: Validation Round-Trip**
    - **Validates: Requirements 3.2, 4.1**
  
  - [ ]* 6.5 Écrire le test property-based pour la pagination
    - **Property 6: Pagination Correctness**
    - **Validates: Requirements 4.1, 4.3**

- [x] 7. Implémenter les endpoints API
  - [x] 7.1 Créer les schemas de réponse
    - Créer `cmv_ml/app/schemas/predictions.py`
    - Définir PredictionResponse, ValidatedPredictionSchema, PaginatedPredictions
    - _Requirements: 3.1, 4.2_
  
  - [x] 7.2 Créer le router des prédictions
    - Créer `cmv_ml/app/routers/predictions.py`
    - Implémenter POST `/predict` avec validation, prédiction, cache, et note RGPD dans la doc
    - Implémenter POST `/predictions/{id}/validate` avec vérification cache et persistance
    - Implémenter GET `/predictions` avec pagination
    - _Requirements: 1.1, 1.6, 3.1, 3.2, 3.5, 4.1, 4.2, 4.3, 8.4_
  
  - [x] 7.3 Créer le point d'entrée de l'application
    - Créer `cmv_ml/app/main.py` avec lifespan pour charger le modèle au démarrage
    - Configurer CORS et les gestionnaires d'erreurs
    - _Requirements: 6.1, 6.2_

- [x] 8. Checkpoint - Vérifier l'API complète
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implémenter SHAP (optionnel)
  - [x] 9.1 Créer le SHAP Explainer
    - Créer `cmv_ml/app/services/shap_explainer.py`
    - Implémenter `explain()` qui retourne les contributions SHAP par feature
    - Gérer le cas où SHAP est désactivé via config
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 9.2 Intégrer SHAP dans l'endpoint /predict
    - Ajouter le paramètre `explain: bool = Query(False)`
    - Appeler SHAP_Explainer si explain=true et SHAP_ENABLED
    - _Requirements: 5.1, 5.3_
  
  - [ ]* 9.3 Écrire le test property-based pour SHAP
    - **Property 7: SHAP Feature Coverage**
    - **Validates: Requirements 5.2**

- [x] 10. Intégration Docker Compose
  - [x] 10.1 Créer les migrations Alembic
    - Créer `cmv_ml/alembic.ini` et `cmv_ml/alembic/` basés sur cmv_patients
    - Créer la migration initiale pour la table validated_predictions
    - _Requirements: 7.3_
  
  - [x] 10.2 Mettre à jour docker-compose.yml
    - Ajouter le service `db_ml` (PostgreSQL) sur le port 6004
    - Ajouter le service `api_ml` sur le port 8004
    - Configurer les variables d'environnement (DATABASE_URL, SECRET_KEY, ALGORITHM, MODEL_PATH)
    - Ajouter le volume pour le fichier modèle
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 10.3 Mettre à jour la configuration du Gateway
    - Ajouter ML_SERVICE dans `cmv_gateway/cmv_back/app/utils/config.py`
    - _Requirements: 7.4_

- [x] 11. Checkpoint final - Vérifier l'intégration complète
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées avec `*` sont optionnelles (tests property-based)
- Le modèle XGBoost doit être fourni séparément (fichier .json ou .joblib)
- Les features médicales ne sont JAMAIS persistées (conformité RGPD)
- Le service utilise le même système JWT que les autres microservices
