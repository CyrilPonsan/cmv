# Plan d'Implémentation : Migration Redis vers Valkey

## Vue d'ensemble

Migration minimale de Redis vers Valkey : remplacement de l'image Docker, mise à jour des variables d'environnement, nettoyage du code mort, et adaptation des tests. Le package Python `redis` est conservé (compatible Valkey).

## Tâches

- [x] 1. Remplacer l'image Docker Redis par Valkey dans les fichiers Compose
  - [x] 1.1 Modifier `docker-compose.yml` : remplacer `image: redis:latest` par `image: valkey/valkey:latest`
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.2 Modifier `dev-docker-compose.yml` : remplacer `image: redis:latest` par `image: valkey/valkey:latest`
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.3 Modifier `preprod-docker-compose.yml` : remplacer `image: redis:latest` par `image: valkey/valkey:latest`
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.4 Renommer `redis-compose.yml` en `valkey-compose.yml` et remplacer l'image par `valkey/valkey:latest`
    - _Requirements: 6.1, 6.2_

- [x] 2. Mettre à jour les variables d'environnement et la configuration du Gateway
  - [x] 2.1 Modifier `.env` : renommer `REDIS_HOST` en `VALKEY_HOST` et `REDIS_PORT` en `VALKEY_PORT`
    - _Requirements: 2.1_
  - [x] 2.2 Modifier `cmv_gateway/cmv_back/app/utils/config.py` : ajouter l'export de `VALKEY_HOST` et `VALKEY_PORT` depuis les variables d'environnement (avec valeurs par défaut `localhost` et `6379`)
    - _Requirements: 2.2_
  - [x] 2.3 Modifier `cmv_gateway/cmv_back/app/dependancies/redis.py` : construire l'URL de connexion à partir de `VALKEY_HOST` et `VALKEY_PORT` au lieu d'URLs codées en dur
    - _Requirements: 3.1, 3.2_

- [x] 3. Checkpoint - Vérifier que le Gateway se connecte correctement
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Nettoyer le code mort Redis dans les services Patients et Chambres
  - [x] 4.1 Supprimer `cmv_patients/app/dependancies/redis.py`
    - _Requirements: 4.1_
  - [x] 4.2 Supprimer l'import `from .redis import redis_client` et l'alias `redis = redis_client` dans `cmv_patients/app/dependancies/auth.py`
    - _Requirements: 4.2_
  - [x] 4.3 Supprimer `cmv_chambres/app/dependancies/redis.py`
    - _Requirements: 4.3_
  - [x] 4.4 Retirer `fakeredis` de `cmv_patients/requirements.txt` et `cmv_chambres/requirements.txt`
    - _Requirements: 4.4_

- [x] 5. Mettre à jour les fixtures de test
  - [x] 5.1 Supprimer la fixture `redis_client` et l'import `from redis.asyncio import Redis` dans `cmv_patients/app/tests/conftest.py`
    - _Requirements: 5.2, 5.3_
  - [x] 5.2 Vérifier que le mock Redis dans `cmv_gateway/cmv_back/app/tests/conftest.py` est toujours fonctionnel (aucune modification attendue)
    - _Requirements: 5.1_

- [x] 6. Checkpoint - Vérifier la non-régression
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Écrire le test property-based pour le round-trip clé-valeur
  - [x] 7.1 Ajouter `hypothesis` dans `cmv_gateway/cmv_back/requirements.txt`
    - _Requirements: 3.3, 3.4_
  - [x] 7.2 Créer `cmv_gateway/cmv_back/app/tests/test_valkey_properties.py` avec un test property-based utilisant `hypothesis` et `fakeredis`
    - **Property 1: Round-trip des opérations clé-valeur**
    - **Validates: Requirements 3.3, 3.4**
    - Générer des paires clé-valeur aléatoires (sessions `session:{id}` et tokens blacklistés `blacklist:{token}`)
    - Stocker avec `setex`, récupérer avec `get`, vérifier l'égalité
    - Configurer minimum 100 itérations

- [x] 8. Checkpoint final - Vérifier que tous les tests passent
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Le package Python `redis` est conservé — seule l'image Docker change
- Les noms de service Docker (`redis`) restent inchangés dans les fichiers multi-services pour préserver le réseau interne
- `fakeredis` est conservé dans `cmv_gateway/cmv_back/requirements.txt` pour les tests (mock Redis)
