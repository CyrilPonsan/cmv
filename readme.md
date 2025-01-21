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

## Démarrage

Pour lancer l'application en mode développement :

```bash
npm run start:dev
```

## Contribution

Pour contribuer au projet, veuillez consulter le dépôt GitHub : [https://github.com/CyrilPonsan/cmv](https://github.com/CyrilPonsan/cmv)
