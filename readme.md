# CMV - Application de Gestion

## Description

Système d'information pour la clinique fictive Montvert : Ce dépôt inclue l'interface utilisateur, la partie back-end avec une architecture de microservices.

## Prérequis

- Docker et Docker Compose
- Node.js 20.x
- npm
- Git
- Python 3.12, conseillé : 3.13
  L'application n'a pas été testée avec d'autres versions de Python.
  Dans le cas où vous souhaitez l'installer avec la version 3.12, vous devez modifier les commandes npm ci-dessous pour correspondre à la version 3.12 :
- `npm run set-venv`
- `npm run set-env`
- `npm run install:app`

## Installation

1. Cloner le dépôt :

```bash
git clone git@github.com:CyrilPonsan/cmv.git
```

2. Naviguer vers le répertoire du projet :

```bash
cd cmv
```

3. Créer les environnements virtuels :

```bash
npm run set-venv
```

4. Configurer les fichiers d'environnement :

```bash
npm run set-env
```

Cette commande va créer plusieurs fichiers d'environnement avec des valeurs exemples dans les répertoires suivants :

- À la racine du projet
- `./cmv_chambres`
- `./cmv_gateway/cmv_back`
- `./cmv_gateway/cmv_front`
- `./cmv_patients`

> **Important** : Les valeurs des clés AWS dans le fichier d'environnement à la racine du projet et dans `cmv_patients` doivent être remplacées par des valeurs valides pour que l'application fonctionne correctement dans tous les environnements (développement, préproduction, production).

5. Installer les dépendances :

```bash
npm run Install:app
```

## Tests frontend

```bash
cd cmv_gateway/cmv_front
npm run test:unit
```

## Tests API Gateway

```bash
cd cmv_gateway/cmv_back
docker compose up --build
docker compose down
```

## Tests API Patients

Avant de lancer les tests, assurez vous de démonter les conteneurs existants avec la commande suivante :

```bash
docker compose -f preprod-docker-compose.yml down
```

```bash
cd cmv_patients
docker compose up --build
docker compose down
```

## Tests API Chambres

```bash
cd cmv_chambres
docker compose up --build
docker compose down
```

## Démarrage

Pour lancer l'application en mode développement :

```bash
npm run start:dev
```

Pour lancer l'application en mode préproduction :

```bash
npm run start:preprod
```

## Bases de données des différentes API

Les bases de données sont créées automatiquement lors du lancement de l'application en mode développement ou en mode préproduction. Les bases de données des microservices sont accessibles sur les port 6001, 6002 et 6003.
Les identifiants de connexion des bases de données sont disponibles dans les fichiers d'environnement des microservices.
L'url de connexion des bases de données des microservices est accessible dans les fichiers d'environnement des microservices,les identifiants de connexion présents dans l'url sont ceux pour un "rôle" utilisateur postgresql.
Les identifiants indiqués à la suite de l'url sont ceux pour un "rôle" admin postgresql.
Il est prudent de créer un rôle utilisateur avec des droits limités en se référent à la documentation de postgresql.

## Contribution

Pour contribuer au projet, veuillez consulter le dépôt GitHub : [https://github.com/CyrilPonsan/cmv](https://github.com/CyrilPonsan/cmv)
