# Plan d'Implémentation : Sécurisation des Secrets et Configuration

## Vue d'ensemble

Migration progressive des quatre microservices FastAPI (cmv_gateway, cmv_patients, cmv_chambres, cmv_ml) depuis `os.getenv()` vers `pydantic-settings` (BaseSettings), avec épinglage des dépendances. Les fichiers `.env` existants sont conservés tels quels (environnement de test avec BDD jetables). Chaque tâche est incrémentale et s'appuie sur les précédentes.

## Tâches

- [ ] 1. Migration de cmv_chambres vers BaseSettings
  - [x] 1.1 Réécrire `cmv_chambres/app/utils/config.py` avec `ChambresSettings`
    - Remplacer `os.getenv()` par une classe `ChambresSettings(BaseSettings)` avec validation Pydantic
    - Champs obligatoires : `CHAMBRES_DATABASE_URL`, `SECRET_KEY`
    - Champs avec défaut : `ALGORITHM="HS256"`, `ENVIRONMENT` (Literal["dev", "staging", "production"], défaut "dev")
    - Ajouter `field_validator` pour valider le format PostgreSQL de `CHAMBRES_DATABASE_URL`
    - Ajouter validation renforcée en production via `model_post_init` (SECRET_KEY ≥ 32 chars, rejet valeurs faibles)
    - Exporter les aliases `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ENVIRONMENT` pour compatibilité
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.1, 5.2, 7.1, 7.2, 7.4_

  - [ ]* 1.2 Écrire les tests unitaires pour `ChambresSettings`
    - Tester l'instanciation réussie avec des variables valides
    - Tester le rejet de chaque variable obligatoire manquante
    - Tester le rejet d'URLs PostgreSQL invalides (exemples concrets)
    - Tester le comportement SECRET_KEY en production vs dev
    - Tester les valeurs par défaut
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 1.3 Écrire le test de propriété — Rejet des URLs PostgreSQL invalides (Propriété 1)
    - **Propriété 1 : Pour toute chaîne ne commençant pas par `postgresql://` ou `postgresql+asyncpg://`, l'instanciation doit lever une ValidationError**
    - **Valide : Exigences 3.3, 3.5**

  - [ ]* 1.4 Écrire le test de propriété — Rejet des SECRET_KEY faibles en production (Propriété 4)
    - **Propriété 4 : Pour toute valeur de SECRET_KEY appartenant aux valeurs faibles connues avec ENVIRONMENT="production", l'instanciation doit lever une ValidationError**
    - **Valide : Exigences 7.2, 7.4**

  - [ ]* 1.5 Écrire le test de propriété — Rejet des SECRET_KEY trop courtes en production (Propriété 5)
    - **Propriété 5 : Pour toute chaîne de longueur < 32 avec ENVIRONMENT="production", l'instanciation doit lever une ValidationError**
    - **Valide : Exigences 7.1, 7.4**

  - [ ]* 1.6 Écrire le test de propriété — Acceptation des configurations valides (Propriété 6)
    - **Propriété 6 : Pour tout ensemble de variables valides, l'instanciation doit réussir sans exception**
    - **Valide : Exigences 3.1, 3.4**

  - [ ]* 1.7 Écrire le test de propriété — Priorité variable système sur fichier .env (Propriété 7)
    - **Propriété 7 : Pour toute variable définie à la fois dans .env et comme variable système, la valeur système prévaut**
    - **Valide : Exigence 5.3**

  - [ ]* 1.8 Écrire le test de propriété — Valeurs par défaut pour les variables optionnelles (Propriété 8)
    - **Propriété 8 : Sans fournir les variables optionnelles, les valeurs par défaut du modèle sont utilisées**
    - **Valide : Exigence 3.4**

- [ ] 2. Migration de cmv_gateway vers BaseSettings
  - [x] 2.1 Réécrire `cmv_gateway/cmv_back/app/utils/config.py` avec `GatewaySettings`
    - Remplacer `os.getenv()` par une classe `GatewaySettings(BaseSettings)` avec validation Pydantic
    - Champs obligatoires : `GATEWAY_DATABASE_URL`, `SECRET_KEY`, `PATIENTS_SERVICE`, `CHAMBRES_SERVICE`, `ML_SERVICE`
    - Champs avec défaut : `ALGORITHM="HS256"`, `ACCESS_MAX_AGE=30`, `REFRESH_MAX_AGE=1440`, `ENVIRONMENT="dev"`, `VALKEY_HOST="redis"`, `VALKEY_PORT=6379`, `TEST_DATABASE_URL="sqlite:///:memory:"`
    - Ajouter `field_validator` pour URLs PostgreSQL et URLs de services (http/https)
    - Ajouter validation renforcée en production via `model_post_init`
    - Exporter les aliases pour compatibilité avec le code existant
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 7.1, 7.2, 7.4_

  - [ ]* 2.2 Écrire les tests unitaires pour `GatewaySettings`
    - Tester l'instanciation réussie avec des variables valides
    - Tester le rejet de chaque variable obligatoire manquante
    - Tester le rejet d'URLs de services invalides
    - Tester le rejet d'URLs PostgreSQL invalides
    - _Exigences : 3.1, 3.2, 3.3, 6.1, 6.2, 6.3_

  - [ ]* 2.3 Écrire le test de propriété — Rejet des URLs de services invalides (Propriété 2)
    - **Propriété 2 : Pour toute chaîne ne commençant pas par `http://` ou `https://`, l'instanciation de GatewaySettings avec cette URL de service doit lever une ValidationError**
    - **Valide : Exigences 6.2, 6.3**

- [x] 3. Checkpoint — Vérifier la migration Gateway et Chambres
  - Exécuter tous les tests pour cmv_gateway et cmv_chambres. Vérifier que les services démarrent correctement avec les fichiers `.env` existants. Poser des questions à l'utilisateur si nécessaire.

- [ ] 4. Migration de cmv_patients vers BaseSettings
  - [x] 4.1 Réécrire `cmv_patients/app/utils/config.py` avec `PatientsSettings`
    - Remplacer `os.getenv()` par une classe `PatientsSettings(BaseSettings)` avec validation Pydantic
    - Champs obligatoires : `PATIENTS_DATABASE_URL`, `SECRET_KEY`, `AWS_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `CHAMBRES_SERVICE`
    - Champs avec défaut : `ALGORITHM="HS256"`, `ENVIRONMENT="dev"`
    - Ajouter `field_validator` pour URL PostgreSQL et URL de service CHAMBRES_SERVICE
    - Ajouter validation renforcée en production via `model_post_init`
    - Exporter les aliases pour compatibilité
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.1, 5.2, 6.2, 6.3, 6.4, 7.1, 7.2, 7.4_

  - [ ]* 4.2 Écrire les tests unitaires pour `PatientsSettings`
    - Tester l'instanciation réussie avec des variables valides
    - Tester le rejet de chaque variable obligatoire manquante (y compris AWS_*)
    - Tester le rejet d'URLs invalides
    - _Exigences : 3.1, 3.2, 6.4_

- [ ] 5. Migration de cmv_ml vers BaseSettings
  - [x] 5.1 Réécrire `cmv_ml/app/utils/config.py` avec `MLSettings`
    - Remplacer `os.getenv()` par une classe `MLSettings(BaseSettings)` avec validation Pydantic
    - Champs obligatoires : `ML_DATABASE_URL`, `SECRET_KEY`, `HMAC`
    - Champs avec défaut : `ALGORITHM="HS256"`, `ENVIRONMENT="dev"`, `MODEL_PATH="./models/model.ubj"`, `SHAP_ENABLED=False`
    - Ajouter `field_validator` pour URL PostgreSQL et format HMAC (64 hex chars)
    - Ajouter validation renforcée en production via `model_post_init`
    - Exporter les aliases pour compatibilité
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.1, 5.2, 7.1, 7.2, 7.3, 7.4_

  - [ ]* 5.2 Écrire les tests unitaires pour `MLSettings`
    - Tester l'instanciation réussie avec des variables valides
    - Tester le rejet de HMAC invalide (trop court, trop long, caractères non-hex)
    - Tester le rejet d'URLs PostgreSQL invalides
    - _Exigences : 3.1, 3.3, 7.3_

  - [ ]* 5.3 Écrire le test de propriété — Validation HMAC (Propriété 3)
    - **Propriété 3 : Pour toute chaîne qui n'est pas exactement 64 caractères hexadécimaux, l'instanciation de MLSettings doit lever une ValidationError**
    - **Valide : Exigences 7.3, 7.4**

- [x] 6. Checkpoint — Vérifier la migration de tous les services
  - Exécuter tous les tests pour les quatre microservices. Vérifier que chaque service démarre correctement avec son fichier `.env`. Poser des questions à l'utilisateur si nécessaire.

- [ ] 7. Épinglage des dépendances
  - [x] 7.1 Épingler les dépendances de production dans `cmv_gateway/cmv_back/requirements.txt`
    - Remplacer les dépendances non épinglées par des versions exactes au format `package==X.Y.Z`
    - Ajouter `pydantic-settings` comme dépendance de production
    - Retirer `python-dotenv` (transitive via pydantic-settings), `faker`, `pytest`, `pytest-*`, `hypothesis`, `fakeredis` (déplacés vers dev)
    - _Exigences : 4.1, 4.3_

  - [x] 7.2 Créer `cmv_gateway/cmv_back/requirements-dev.txt`
    - Inclure `-r requirements.txt` en première ligne
    - Ajouter les dépendances de test épinglées : `faker`, `pytest`, `pytest-asyncio`, `pytest-mock`, `pytest-httpx`, `hypothesis`, `fakeredis`
    - _Exigences : 4.2_

  - [x] 7.3 Épingler les dépendances de production dans `cmv_patients/requirements.txt`
    - Même approche : versions exactes, ajout de `pydantic-settings`, séparation prod/test
    - _Exigences : 4.1, 4.3_

  - [x] 7.4 Créer `cmv_patients/requirements-dev.txt`
    - Inclure `-r requirements.txt` et les dépendances de test épinglées
    - _Exigences : 4.2_

  - [x] 7.5 Épingler les dépendances de production dans `cmv_chambres/requirements.txt`
    - Même approche : versions exactes, ajout de `pydantic-settings`, séparation prod/test
    - _Exigences : 4.1, 4.3_

  - [x] 7.6 Créer `cmv_chambres/requirements-dev.txt`
    - Inclure `-r requirements.txt` et les dépendances de test épinglées
    - _Exigences : 4.2_

  - [x] 7.7 Épingler les dépendances de production dans `cmv_ml/requirements.txt`
    - Même approche : versions exactes, ajout de `pydantic-settings`, séparation prod/test
    - _Exigences : 4.1, 4.3_

  - [x] 7.8 Créer `cmv_ml/requirements-dev.txt`
    - Inclure `-r requirements.txt` et les dépendances de test épinglées
    - _Exigences : 4.2_

- [x] 8. Checkpoint final — Validation complète
  - Vérifier que tous les tests passent pour les quatre microservices. Vérifier que les `requirements.txt` sont correctement épinglés et que les `requirements-dev.txt` existent. Poser des questions à l'utilisateur si nécessaire.

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être ignorées pour un MVP plus rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints assurent une validation incrémentale
- Les tests de propriétés valident les propriétés universelles de correction définies dans le document de conception
- Les tests unitaires valident des exemples concrets et des cas limites
- Les aliases dans chaque `config.py` garantissent la compatibilité avec le code existant sans modification des imports
- Les fichiers `.env` existants sont conservés et versionnés (environnement de test avec BDD jetables)
