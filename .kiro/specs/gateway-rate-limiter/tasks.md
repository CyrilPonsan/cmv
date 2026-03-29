# Plan d'implémentation : Rate Limiting sur la Gateway

## Vue d'ensemble

Implémentation du rate limiting sur la gateway FastAPI en utilisant `fastapi-limiter` avec Valkey comme backend. Le plan suit une approche incrémentale : d'abord le module utilitaire avec l'identification client et les callbacks, puis l'intégration dans le cycle de vie de l'application, l'application des limites sur les endpoints, et enfin les tests.

## Tâches

- [x] 1. Créer le module utilitaire `rate_limiter.py`
  - [x] 1.1 Créer le fichier `cmv_gateway/cmv_back/app/utils/rate_limiter.py` avec les constantes de configuration
    - Définir `LOGIN_RATE_LIMIT_TIMES = 5`, `LOGIN_RATE_LIMIT_SECONDS = 60`, `GLOBAL_RATE_LIMIT_TIMES = 60`, `GLOBAL_RATE_LIMIT_SECONDS = 60`
    - Importer `VALKEY_HOST`, `VALKEY_PORT` depuis `app.utils.config`
    - _Exigences : 2.1, 3.1_

  - [x] 1.2 Implémenter la fonction `custom_identifier(request: Request) -> str`
    - Extraire l'IP depuis l'en-tête `X-Forwarded-For` (première IP) si présent
    - Sinon utiliser `request.client.host`
    - Retourner `"unknown"` avec journalisation d'un avertissement si l'IP ne peut être déterminée
    - _Exigences : 6.1, 6.2, 6.3_

  - [x] 1.3 Implémenter la fonction `custom_callback(request, response, pexpire)`
    - Calculer `Retry-After` en secondes depuis `pexpire` (millisecondes)
    - Lever `HTTPException(429)` avec corps JSON `{"detail": "Trop de requêtes. Réessayez dans X secondes."}`
    - Ajouter les en-têtes `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
    - _Exigences : 2.2, 2.3, 4.1, 4.2_

  - [x] 1.4 Implémenter `init_rate_limiter() -> bool` et `close_rate_limiter()`
    - Créer un client Redis asynchrone vers `redis://{VALKEY_HOST}:{VALKEY_PORT}`
    - Appeler `FastAPILimiter.init()` avec le client, l'identifier et le callback
    - Capturer `ConnectionError` et `TimeoutError`, journaliser et retourner `False` en cas d'échec
    - `close_rate_limiter()` ferme proprement la connexion Redis
    - _Exigences : 1.1, 1.3, 5.1, 5.2_

  - [x] 1.5 Écrire le test de propriété pour l'identification client
    - **Propriété 5 : Identification client par IP**
    - **Valide : Exigences 6.1, 6.2**

- [x] 2. Checkpoint — Vérifier le module utilitaire
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Intégrer le rate limiter dans le cycle de vie de l'application
  - [x] 3.1 Modifier `cmv_gateway/cmv_back/app/main.py` pour ajouter le `lifespan`
    - Importer `init_rate_limiter` et `close_rate_limiter` depuis `app.utils.rate_limiter`
    - Créer un `@asynccontextmanager` `lifespan(app)` qui appelle `init_rate_limiter()` au startup et `close_rate_limiter()` au shutdown
    - Passer `lifespan=lifespan` au constructeur `FastAPI()`
    - _Exigences : 1.1, 1.2_

  - [x] 3.2 Appliquer la limite globale sur le routeur `/api`
    - Modifier `cmv_gateway/cmv_back/app/routers/api.py` pour ajouter `dependencies=[Depends(RateLimiter(times=60, seconds=60))]` au routeur principal
    - _Exigences : 3.1, 3.2_

  - [x] 3.3 Appliquer la limite stricte sur le endpoint login
    - Modifier `cmv_gateway/cmv_back/app/routers/auth.py` pour ajouter `Depends(RateLimiter(times=5, seconds=60))` comme dépendance du endpoint `POST /api/auth/login`
    - _Exigences : 2.1, 3.3_

- [x] 4. Checkpoint — Vérifier l'intégration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implémenter la résilience en cas d'indisponibilité de Valkey
  - [x] 5.1 Ajouter la gestion du mode dégradé dans `custom_identifier` et `custom_callback`
    - Wrapper les appels Redis dans des blocs try/except pour capturer les erreurs de connexion
    - En cas d'erreur, laisser passer la requête sans limitation (fail-open)
    - Journaliser un avertissement indiquant que le rate limiting est temporairement désactivé
    - _Exigences : 5.1, 5.2, 5.3_

- [x] 6. Écrire les tests unitaires et de propriétés
  - [x] 6.1 Créer `cmv_gateway/cmv_back/app/tests/test_rate_limiter.py` avec les fixtures de base
    - Configurer `fakeredis.aioredis.FakeRedis` pour simuler Valkey
    - Réutiliser les patterns existants de `conftest.py` (`ac`, `mock_redis`)
    - _Exigences : 1.1, 1.2_

  - [x] 6.2 Écrire le test de propriété pour la limitation du endpoint login
    - **Propriété 1 : Limitation stricte du endpoint login**
    - **Valide : Exigences 2.1, 2.2, 2.3**

  - [x] 6.3 Écrire le test de propriété pour la limitation globale
    - **Propriété 2 : Limitation globale des endpoints API**
    - **Valide : Exigences 3.1, 3.2**

  - [x] 6.4 Écrire le test de propriété pour la priorité des limites spécifiques
    - **Propriété 3 : Priorité des limites spécifiques sur la limite globale**
    - **Valide : Exigence 3.3**

  - [x] 6.5 Écrire le test de propriété pour le format de la réponse 429
    - **Propriété 4 : Format de la réponse 429**
    - **Valide : Exigences 4.1, 4.2**

  - [x] 6.6 Écrire les tests unitaires pour le mode dégradé et la résilience
    - Tester l'initialisation quand Valkey est down (mode dégradé au démarrage)
    - Tester la panne Valkey en cours d'exécution (fail-open)
    - Tester la reprise automatique après retour de Valkey
    - Tester le fallback IP inconnue (`request.client = None`)
    - _Exigences : 1.3, 5.1, 5.2, 5.3, 6.3_

- [x] 7. Checkpoint final — Vérifier que tous les tests passent
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées `*` sont optionnelles et peuvent être ignorées pour un MVP rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints permettent une validation incrémentale
- Les tests de propriétés valident les propriétés de correction universelles définies dans le design
- Les tests unitaires couvrent les cas spécifiques et les edge cases
- `fakeredis` est utilisé pour simuler Valkey dans les tests (pattern existant dans le projet)
