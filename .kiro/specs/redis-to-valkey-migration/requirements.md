# Document d'Exigences

## Introduction

Ce document décrit les exigences pour la migration de Redis vers Valkey dans l'application CMV (microservices). La motivation principale est une vulnérabilité de sécurité dans l'image Docker Redis. Valkey, maintenu par la Linux Foundation, est un remplacement direct de Redis (même protocole, même API, même port). Le périmètre de la migration est volontairement minimal pour limiter les risques de régression, dans le cadre d'un projet de master présenté devant un jury.

## Glossaire

- **CMV** : L'application microservices composée de trois services (Gateway, Patients, Chambres)
- **Gateway** : Le service `cmv_gateway` (Python/FastAPI) qui gère l'authentification, les sessions et le routage
- **Service_Patients** : Le service `cmv_patients` (Python/FastAPI) qui gère les données patients
- **Service_Chambres** : Le service `cmv_chambres` (Python/FastAPI) qui gère les données des chambres
- **Valkey** : Fork open-source de Redis maintenu par la Linux Foundation, compatible protocole Redis
- **Fichiers_Compose** : Les fichiers Docker Compose du projet (`docker-compose.yml`, `dev-docker-compose.yml`, `preprod-docker-compose.yml`, `redis-compose.yml`)
- **Client_Redis** : Le module Python `redis` (redis-py) utilisé pour la connexion asynchrone au serveur
- **Code_Mort** : Code importé ou déclaré mais jamais utilisé dans le flux d'exécution d'un service
- **Session** : Donnée stockée dans Valkey avec la clé `session:{session_id}` et une expiration d'une heure
- **Token_Blacklisté** : Token JWT invalidé stocké dans Valkey avec la clé `blacklist:{token}` et une expiration d'une heure

## Exigences

### Exigence 1 : Remplacement de l'image Docker Redis par Valkey

**User Story :** En tant que développeur, je veux remplacer l'image Docker `redis:latest` par `valkey/valkey:latest` dans tous les fichiers Compose, afin de résoudre la vulnérabilité de sécurité identifiée.

#### Critères d'acceptation

1. QUAND les Fichiers_Compose sont modifiés, LE Système SHALL remplacer l'image `redis:latest` par `valkey/valkey:latest` dans `docker-compose.yml`, `dev-docker-compose.yml`, `preprod-docker-compose.yml` et `redis-compose.yml`
2. QUAND le conteneur Valkey démarre, LE Système SHALL conserver le nom de conteneur `redis-server` et le mappage de port `6379:6379` pour assurer la compatibilité réseau
3. QUAND le conteneur Valkey démarre, LE Système SHALL monter le volume de données existant pour préserver la persistance

### Exigence 2 : Mise à jour des variables d'environnement

**User Story :** En tant que développeur, je veux renommer les variables d'environnement Redis en Valkey, afin que la configuration reflète la technologie utilisée.

#### Critères d'acceptation

1. QUAND le fichier `.env` est modifié, LE Système SHALL renommer `REDIS_HOST` en `VALKEY_HOST` et `REDIS_PORT` en `VALKEY_PORT` en conservant les mêmes valeurs
2. QUAND les fichiers de configuration Python lisent les variables d'environnement, LE Système SHALL référencer `VALKEY_HOST` et `VALKEY_PORT` au lieu de `REDIS_HOST` et `REDIS_PORT`

### Exigence 3 : Maintien de la compatibilité du client Python

**User Story :** En tant que développeur, je veux que le client Python Redis continue de fonctionner avec Valkey, afin de minimiser les changements de code et les risques de régression.

#### Critères d'acceptation

1. LE Gateway SHALL continuer à utiliser le package Python `redis` (redis-py) pour se connecter à Valkey, car Valkey supporte le protocole `redis://`
2. QUAND le fichier `cmv_gateway/cmv_back/app/dependancies/redis.py` est modifié, LE Gateway SHALL construire l'URL de connexion à partir des variables d'environnement `VALKEY_HOST` et `VALKEY_PORT` au lieu de valeurs codées en dur
3. QUAND le Gateway se connecte à Valkey, LE Gateway SHALL maintenir le fonctionnement de la gestion des sessions (clés `session:{session_id}`) sans modification de la logique métier
4. QUAND le Gateway se connecte à Valkey, LE Gateway SHALL maintenir le fonctionnement du blacklisting de tokens (clés `blacklist:{token}`) sans modification de la logique métier

### Exigence 4 : Nettoyage du code mort Redis dans les services Patients et Chambres

**User Story :** En tant que développeur, je veux supprimer le code Redis inutilisé dans les services Patients et Chambres, afin de réduire la dette technique et clarifier l'architecture.

#### Critères d'acceptation

1. QUAND le Service_Patients est nettoyé, LE Système SHALL supprimer le fichier `cmv_patients/app/dependancies/redis.py` qui constitue du Code_Mort
2. QUAND le Service_Patients est nettoyé, LE Système SHALL supprimer l'import et l'alias `redis_client` dans `cmv_patients/app/dependancies/auth.py` qui ne sont jamais utilisés dans la logique d'authentification
3. QUAND le Service_Chambres est nettoyé, LE Système SHALL supprimer le fichier `cmv_chambres/app/dependancies/redis.py` qui constitue du Code_Mort
4. QUAND la dépendance `fakeredis` est présente dans les fichiers `requirements.txt` des services Patients et Chambres, LE Système SHALL la retirer si aucun test ne l'utilise

### Exigence 5 : Mise à jour des fixtures de test

**User Story :** En tant que développeur, je veux que les tests continuent de fonctionner après la migration, afin de garantir la non-régression.

#### Critères d'acceptation

1. QUAND les tests du Gateway sont exécutés, LE Système SHALL conserver le mock Redis existant dans `cmv_gateway/cmv_back/app/tests/conftest.py` qui fonctionne indépendamment du serveur
2. QUAND les tests du Service_Patients sont nettoyés, LE Système SHALL supprimer la fixture `redis_client` inutilisée dans `cmv_patients/app/tests/conftest.py`
3. QUAND les tests du Service_Patients sont nettoyés, LE Système SHALL supprimer l'import `from redis.asyncio import Redis` devenu inutile dans `cmv_patients/app/tests/conftest.py`

### Exigence 6 : Renommage du fichier Compose dédié

**User Story :** En tant que développeur, je veux renommer `redis-compose.yml` en `valkey-compose.yml`, afin que le nom du fichier reflète la technologie utilisée.

#### Critères d'acceptation

1. QUAND le fichier est renommé, LE Système SHALL créer `valkey-compose.yml` avec l'image `valkey/valkey:latest` et supprimer `redis-compose.yml`
2. QUAND le fichier `valkey-compose.yml` est créé, LE Système SHALL conserver la même configuration de service (port, restart policy) que l'ancien fichier
