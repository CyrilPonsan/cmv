# Document d'Exigences — Rate Limiting sur la Gateway

## Introduction

La gateway API (`cmv_gateway/cmv_back`) expose des endpoints d'authentification et de gestion de données médicales. Actuellement, aucun mécanisme de rate limiting n'est en place malgré la présence de la dépendance `fastapi-limiter` et d'un handler pour les erreurs HTTP 429. Cette fonctionnalité vise à protéger l'API contre les abus, en priorité le endpoint de connexion (`/api/auth/login`) contre les attaques par force brute, puis les autres endpoints selon des limites adaptées à leur usage.

## Glossaire

- **Gateway** : Le microservice FastAPI (`cmv_gateway/cmv_back`) servant de point d'entrée unique pour l'application.
- **Rate_Limiter** : Le composant logiciel responsable du comptage et de la limitation des requêtes par client, basé sur la bibliothèque `fastapi-limiter`.
- **Valkey** : Le serveur de stockage clé-valeur compatible Redis utilisé comme backend pour le comptage des requêtes du Rate_Limiter. Configuré via `VALKEY_HOST` et `VALKEY_PORT`.
- **Endpoint_Login** : Le endpoint POST `/api/auth/login` utilisé pour l'authentification des utilisateurs.
- **Endpoint_Protégé** : Tout endpoint de l'API soumis à une règle de rate limiting.
- **Fenêtre_Temporelle** : La période de temps pendant laquelle les requêtes sont comptabilisées pour un client donné.
- **Identifiant_Client** : L'adresse IP du client utilisée pour identifier de manière unique un appelant aux fins du rate limiting.

## Exigences

### Exigence 1 : Initialisation du Rate Limiter

**User Story :** En tant que développeur, je veux que le Rate_Limiter soit initialisé au démarrage de la Gateway avec Valkey comme backend, afin que le mécanisme de limitation soit opérationnel dès le lancement de l'application.

#### Critères d'acceptation

1. WHEN la Gateway démarre, THE Rate_Limiter SHALL établir une connexion avec Valkey en utilisant les paramètres `VALKEY_HOST` et `VALKEY_PORT` définis dans la configuration.
2. WHEN la Gateway démarre, THE Rate_Limiter SHALL être initialisé via l'événement `lifespan` de FastAPI avant que les requêtes ne soient acceptées.
3. IF la connexion à Valkey échoue au démarrage, THEN THE Gateway SHALL journaliser l'erreur et démarrer en mode dégradé sans rate limiting actif.

### Exigence 2 : Protection du endpoint de connexion contre le brute force

**User Story :** En tant qu'administrateur système, je veux que le Endpoint_Login soit protégé par un rate limiting strict, afin d'empêcher les attaques par force brute sur les comptes utilisateurs.

#### Critères d'acceptation

1. THE Rate_Limiter SHALL limiter le Endpoint_Login à un maximum de 5 requêtes par Fenêtre_Temporelle de 60 secondes par Identifiant_Client.
2. WHEN un Identifiant_Client dépasse la limite de 5 requêtes sur le Endpoint_Login dans une Fenêtre_Temporelle de 60 secondes, THE Gateway SHALL répondre avec un code HTTP 429 et un message indiquant le temps restant avant la prochaine tentative autorisée.
3. WHEN un Identifiant_Client dépasse la limite sur le Endpoint_Login, THE Gateway SHALL inclure un en-tête `Retry-After` dans la réponse HTTP 429 indiquant le nombre de secondes restantes avant la réinitialisation de la Fenêtre_Temporelle.

### Exigence 3 : Rate limiting global sur les endpoints de l'API

**User Story :** En tant qu'administrateur système, je veux que tous les Endpoint_Protégé de l'API aient une limite de requêtes par défaut, afin de protéger la Gateway contre les abus et la surcharge.

#### Critères d'acceptation

1. THE Rate_Limiter SHALL appliquer une limite par défaut de 60 requêtes par Fenêtre_Temporelle de 60 secondes par Identifiant_Client sur tous les endpoints sous le préfixe `/api`.
2. WHEN un Identifiant_Client dépasse la limite globale sur un Endpoint_Protégé, THE Gateway SHALL répondre avec un code HTTP 429.
3. THE Rate_Limiter SHALL permettre de définir des limites spécifiques par endpoint qui prennent priorité sur la limite globale par défaut.

### Exigence 4 : Réponse HTTP 429 et en-têtes informatifs

**User Story :** En tant que développeur frontend, je veux recevoir des informations claires lorsqu'une requête est limitée, afin de pouvoir afficher un message approprié à l'utilisateur et implémenter un mécanisme de retry.

#### Critères d'acceptation

1. WHEN THE Rate_Limiter rejette une requête, THE Gateway SHALL retourner une réponse HTTP 429 avec un corps JSON contenant un champ `detail` décrivant la raison du rejet.
2. WHEN THE Rate_Limiter rejette une requête, THE Gateway SHALL inclure les en-têtes `X-RateLimit-Limit`, `X-RateLimit-Remaining` et `X-RateLimit-Reset` dans la réponse.
3. THE Gateway SHALL ne pas journaliser les erreurs HTTP 429 dans le logger applicatif (comportement déjà anticipé dans le handler d'exceptions existant).

### Exigence 5 : Résilience en cas d'indisponibilité de Valkey

**User Story :** En tant qu'administrateur système, je veux que la Gateway continue de fonctionner même si Valkey devient indisponible, afin de ne pas bloquer les utilisateurs légitimes.

#### Critères d'acceptation

1. IF Valkey devient indisponible après le démarrage, THEN THE Gateway SHALL continuer à traiter les requêtes sans appliquer de rate limiting.
2. IF Valkey devient indisponible, THEN THE Gateway SHALL journaliser un avertissement indiquant que le rate limiting est temporairement désactivé.
3. WHEN Valkey redevient disponible, THE Rate_Limiter SHALL reprendre automatiquement le comptage des requêtes sans nécessiter un redémarrage de la Gateway.

### Exigence 6 : Identification du client

**User Story :** En tant que développeur, je veux que le Rate_Limiter identifie correctement chaque client, afin que la limitation s'applique de manière équitable par appelant.

#### Critères d'acceptation

1. THE Rate_Limiter SHALL utiliser l'adresse IP du client extraite de la requête HTTP comme Identifiant_Client par défaut.
2. WHEN la requête contient un en-tête `X-Forwarded-For`, THE Rate_Limiter SHALL utiliser la première adresse IP de cet en-tête comme Identifiant_Client.
3. IF l'adresse IP du client ne peut pas être déterminée, THEN THE Rate_Limiter SHALL utiliser une clé de fallback générique et journaliser un avertissement.
