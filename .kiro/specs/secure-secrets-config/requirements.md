# Document d'Exigences — Sécurisation des Secrets et Configuration

## Introduction

Le projet CMV Healthcare est composé de quatre microservices FastAPI (cmv_gateway, cmv_patients, cmv_chambres, cmv_ml). Une revue de code a révélé plusieurs problèmes critiques de sécurité et de maintenabilité liés à la gestion des secrets et de la configuration : secrets versionnés dans Git, absence de validation au démarrage, dépendances non épinglées, configuration identique entre environnements, et URLs de services codées en dur. Ce document définit les exigences pour corriger ces vulnérabilités et mettre en place une gestion de configuration robuste et sécurisée.

## Glossaire

- **Microservice** : Un des quatre services FastAPI du projet CMV (cmv_gateway, cmv_patients, cmv_chambres, cmv_ml)
- **Gestionnaire_Configuration** : Module Python basé sur pydantic BaseSettings responsable du chargement et de la validation des variables d'environnement pour chaque Microservice
- **Secret** : Toute valeur sensible (mot de passe de base de données, clé AWS, clé HMAC, SECRET_KEY JWT) qui ne doit pas être stockée en clair dans le dépôt Git
- **Fichier_Env** : Fichier .env contenant les variables d'environnement pour un Microservice
- **Fichier_Env_Example** : Fichier .env.example contenant des clés de variables d'environnement avec des valeurs fictives servant de modèle pour les développeurs
- **Fichier_Gitignore** : Fichier .gitignore contrôlant les fichiers exclus du suivi Git
- **Fichier_Requirements** : Fichier requirements.txt listant les dépendances Python d'un Microservice
- **Variable_Obligatoire** : Variable d'environnement dont l'absence empêche le démarrage du Microservice
- **Profil_Environnement** : Ensemble de valeurs de configuration spécifiques à un environnement d'exécution (dev, staging, production)

## Exigences

### Exigence 1 : Suppression des secrets du dépôt Git

**User Story :** En tant que développeur, je veux que les secrets soient exclus du dépôt Git, afin de prévenir toute fuite de données sensibles.

#### Critères d'acceptation

1. THE Fichier_Gitignore SHALL exclure tous les fichiers .env à la racine et dans chaque répertoire de Microservice (cmv_gateway/cmv_back/.env, cmv_patients/.env, cmv_chambres/.env, cmv_ml/.env, .env)
2. WHEN un fichier .env est détecté dans l'historique Git, THE Microservice SHALL documenter la procédure de rotation des secrets compromis dans un fichier SECURITY.md à la racine du projet
3. THE Fichier_Gitignore SHALL exclure les patterns `**/.env`, `**/.env.local`, et `**/.env.*.local` pour couvrir tous les fichiers de secrets potentiels

### Exigence 2 : Création de fichiers .env.example

**User Story :** En tant que développeur rejoignant le projet, je veux disposer de fichiers .env.example documentés, afin de configurer mon environnement local sans connaître les valeurs réelles des secrets.

#### Critères d'acceptation

1. THE Fichier_Env_Example SHALL exister à la racine du projet et dans chaque répertoire de Microservice (cmv_gateway/cmv_back/, cmv_patients/, cmv_chambres/, cmv_ml/)
2. THE Fichier_Env_Example SHALL contenir toutes les clés de variables d'environnement requises par le Microservice correspondant avec des valeurs fictives explicites (ex: `SECRET_KEY="changez-moi"`, `POSTGRES_PASSWORD="mot_de_passe_local"`)
3. THE Fichier_Env_Example SHALL contenir un commentaire descriptif au-dessus de chaque variable expliquant son rôle
4. THE Fichier_Env_Example SHALL être versionné dans Git (non exclu par le Fichier_Gitignore)

### Exigence 3 : Validation de la configuration au démarrage

**User Story :** En tant que développeur, je veux que chaque microservice valide sa configuration au démarrage, afin de détecter immédiatement les variables manquantes ou invalides au lieu de subir des erreurs en production.

#### Critères d'acceptation

1. THE Gestionnaire_Configuration SHALL utiliser pydantic BaseSettings pour définir et valider toutes les variables d'environnement de chaque Microservice
2. WHEN une Variable_Obligatoire est absente au démarrage, THE Gestionnaire_Configuration SHALL lever une exception avec un message indiquant le nom de la variable manquante
3. WHEN une variable d'environnement a un format invalide (ex: un port non numérique, une URL mal formée), THE Gestionnaire_Configuration SHALL lever une exception avec un message décrivant l'erreur de validation
4. THE Gestionnaire_Configuration SHALL définir des valeurs par défaut uniquement pour les variables non sensibles et optionnelles (ex: ENVIRONMENT="dev", SHAP_ENABLED="false")
5. THE Gestionnaire_Configuration SHALL valider que DATABASE_URL correspond au format d'une URL PostgreSQL valide
6. THE Gestionnaire_Configuration SHALL remplacer les appels `os.getenv()` existants dans les fichiers config.py des quatre Microservices

### Exigence 4 : Épinglage des dépendances

**User Story :** En tant que développeur, je veux que toutes les dépendances Python soient épinglées à des versions spécifiques, afin de garantir des builds reproductibles et éviter les régressions dues à des mises à jour non contrôlées.

#### Critères d'acceptation

1. THE Fichier_Requirements SHALL spécifier une version exacte pour chaque dépendance au format `package==X.Y.Z` dans les quatre Microservices
2. THE Fichier_Requirements SHALL séparer les dépendances de production des dépendances de test via un fichier requirements-dev.txt dédié dans chaque Microservice
3. WHEN un Fichier_Requirements est modifié, THE Fichier_Requirements SHALL conserver la compatibilité avec Python 3.12


### Exigence 5 : Configuration par environnement

**User Story :** En tant qu'opérateur DevOps, je veux que chaque environnement (dev, staging, production) utilise des valeurs de configuration distinctes, afin d'isoler les environnements et éviter qu'une erreur de configuration en développement n'affecte la production.

#### Critères d'acceptation

1. THE Gestionnaire_Configuration SHALL accepter une variable ENVIRONMENT avec les valeurs autorisées : "dev", "staging", "production"
2. WHEN la variable ENVIRONMENT est définie, THE Gestionnaire_Configuration SHALL charger les valeurs de configuration correspondant au Profil_Environnement sélectionné
3. THE Gestionnaire_Configuration SHALL permettre la surcharge de toute variable de configuration via des variables d'environnement système (priorité : variable système > fichier .env)
4. WHILE le Profil_Environnement est "production", THE Gestionnaire_Configuration SHALL exiger que toutes les variables sensibles (SECRET_KEY, mots de passe de base de données, clés AWS, HMAC) soient définies via des variables d'environnement système et non via un Fichier_Env

### Exigence 6 : Externalisation des URLs de services

**User Story :** En tant que développeur, je veux que les URLs des microservices soient configurables par environnement, afin de pouvoir déployer les services sur différentes infrastructures sans modifier le code.

#### Critères d'acceptation

1. THE Gestionnaire_Configuration du Microservice cmv_gateway SHALL définir les URLs des services PATIENTS_SERVICE, CHAMBRES_SERVICE et ML_SERVICE comme des Variable_Obligatoire validées au démarrage
2. THE Gestionnaire_Configuration SHALL valider que chaque URL de service commence par "http://" ou "https://"
3. WHEN une URL de service est absente ou invalide, THE Gestionnaire_Configuration SHALL lever une exception avec un message identifiant l'URL manquante ou invalide
4. THE Gestionnaire_Configuration du Microservice cmv_patients SHALL définir l'URL CHAMBRES_SERVICE comme une Variable_Obligatoire validée au démarrage

### Exigence 7 : Sécurisation de la clé secrète JWT et de la clé HMAC

**User Story :** En tant que responsable sécurité, je veux que les clés cryptographiques respectent des critères de robustesse minimaux, afin de prévenir les attaques par force brute sur les tokens JWT et les signatures HMAC.

#### Critères d'acceptation

1. WHILE le Profil_Environnement est "production", THE Gestionnaire_Configuration SHALL valider que SECRET_KEY a une longueur minimale de 32 caractères
2. WHILE le Profil_Environnement est "production", THE Gestionnaire_Configuration SHALL rejeter les valeurs de SECRET_KEY connues comme faibles (ex: "cle_tres_secrete", "secret", "changez-moi")
3. WHEN la variable HMAC est définie, THE Gestionnaire_Configuration SHALL valider que la valeur est une chaîne hexadécimale de 64 caractères (256 bits)
4. IF la clé SECRET_KEY ou HMAC ne respecte pas les critères de robustesse en production, THEN THE Gestionnaire_Configuration SHALL empêcher le démarrage du Microservice et afficher un message d'erreur explicite
