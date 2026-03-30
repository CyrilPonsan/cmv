# Requirements Document

## Introduction

Ce document décrit les exigences pour la création d'un projet AWS CDK (TypeScript) dans le répertoire `cdk/` à la racine du projet. L'objectif est de déployer deux instances EC2 (T2.medium et T3.small) avec des volumes EBS chiffrés via KMS, au sein d'un même VPC, chacune avec son propre security group. La configuration du projet CDK repose sur des variables d'environnement chargées depuis un fichier `.env` dans le répertoire `cdk/`.

## Glossary

- **CDK_Stack**: La stack AWS CDK principale qui définit l'ensemble des ressources d'infrastructure à déployer.
- **VPC**: Le Virtual Private Cloud partagé par les deux instances EC2.
- **EC2_Instance_Medium**: L'instance EC2 de type T2.medium.
- **EC2_Instance_Small**: L'instance EC2 de type T3.small.
- **EBS_Volume**: Un volume Elastic Block Store de 30 Go attaché à une instance EC2, chiffré via KMS.
- **KMS_Key**: La clé AWS KMS utilisée pour chiffrer les volumes EBS.
- **Security_Group_Medium**: Le security group dédié à l'instance EC2_Instance_Medium.
- **Security_Group_Small**: Le security group dédié à l'instance EC2_Instance_Small.
- **Env_Loader**: Le module responsable du chargement des variables d'environnement depuis le fichier `cdk/.env`.
- **CDK_App**: Le point d'entrée de l'application CDK qui instancie la stack.

## Requirements

### Requirement 1: Initialisation du projet CDK

**User Story:** En tant que développeur, je veux un projet CDK TypeScript initialisé dans le répertoire `cdk/`, afin de pouvoir définir et déployer l'infrastructure AWS via du code.

#### Acceptance Criteria

1. THE CDK_Stack SHALL être définie dans un projet TypeScript situé dans le répertoire `cdk/` à la racine du projet.
2. THE CDK_App SHALL instancier la CDK_Stack avec le compte AWS et la région AWS lus depuis les variables d'environnement `CDK_DEFAULT_ACCOUNT` et `CDK_DEFAULT_REGION`.
3. THE CDK_Stack SHALL inclure les fichiers standard d'un projet CDK TypeScript : `cdk.json`, `tsconfig.json`, `package.json`, et le fichier source principal de la stack.

### Requirement 2: Chargement des variables d'environnement

**User Story:** En tant que développeur, je veux que le projet CDK charge ses variables de configuration depuis un fichier `cdk/.env`, afin de ne pas coder en dur les valeurs sensibles ou spécifiques à l'environnement.

#### Acceptance Criteria

1. THE Env_Loader SHALL charger les variables d'environnement depuis le fichier `cdk/.env` au démarrage de l'application CDK.
2. THE Env_Loader SHALL suivre le format défini dans le fichier `cdk/.env.example` pour les variables attendues.
3. IF le fichier `cdk/.env` est absent, THEN THE Env_Loader SHALL signaler une erreur explicite indiquant que le fichier est manquant.
4. IF une variable obligatoire (`CDK_DEFAULT_ACCOUNT`, `CDK_DEFAULT_REGION`, `DOMAIN`) est absente du fichier `.env`, THEN THE Env_Loader SHALL signaler une erreur explicite indiquant la variable manquante.

### Requirement 3: Création du VPC partagé

**User Story:** En tant que développeur, je veux un VPC partagé entre les deux instances EC2, afin qu'elles puissent communiquer sur le même réseau.

#### Acceptance Criteria

1. THE CDK_Stack SHALL créer un VPC dédié pour les instances EC2.
2. THE VPC SHALL contenir au moins un sous-réseau public.
3. THE VPC SHALL être partagé entre EC2_Instance_Medium et EC2_Instance_Small.

### Requirement 4: Création de la clé KMS

**User Story:** En tant que développeur, je veux une clé KMS dédiée au chiffrement des volumes EBS, afin de garantir la sécurité des données au repos.

#### Acceptance Criteria

1. THE CDK_Stack SHALL créer une KMS_Key dédiée au chiffrement des volumes EBS.
2. THE KMS_Key SHALL être utilisée pour chiffrer les volumes EBS des deux instances EC2.

### Requirement 5: Déploiement de l'instance EC2 T2.medium

**User Story:** En tant que développeur, je veux déployer une instance EC2 de type T2.medium avec un volume EBS chiffré, afin de disposer d'une machine de calcul sécurisée.

#### Acceptance Criteria

1. THE CDK_Stack SHALL créer une EC2_Instance_Medium de type `t2.medium`.
2. THE EC2_Instance_Medium SHALL être déployée dans le VPC partagé.
3. THE EC2_Instance_Medium SHALL avoir un EBS_Volume de 30 Go chiffré avec la KMS_Key.
4. THE EC2_Instance_Medium SHALL être associée au Security_Group_Medium.

### Requirement 6: Déploiement de l'instance EC2 T3.small

**User Story:** En tant que développeur, je veux déployer une instance EC2 de type T3.small avec un volume EBS chiffré, afin de disposer d'une seconde machine de calcul sécurisée.

#### Acceptance Criteria

1. THE CDK_Stack SHALL créer une EC2_Instance_Small de type `t3.small`.
2. THE EC2_Instance_Small SHALL être déployée dans le VPC partagé.
3. THE EC2_Instance_Small SHALL avoir un EBS_Volume de 30 Go chiffré avec la KMS_Key.
4. THE EC2_Instance_Small SHALL être associée au Security_Group_Small.

### Requirement 7: Security Groups dédiés

**User Story:** En tant que développeur, je veux que chaque instance EC2 ait son propre security group, afin de pouvoir affiner les règles de sécurité réseau indépendamment pour chaque instance.

#### Acceptance Criteria

1. THE CDK_Stack SHALL créer un Security_Group_Medium dédié à l'EC2_Instance_Medium.
2. THE CDK_Stack SHALL créer un Security_Group_Small dédié à l'EC2_Instance_Small.
3. THE Security_Group_Medium SHALL être distinct du Security_Group_Small.
4. THE Security_Group_Medium SHALL appartenir au VPC partagé.
5. THE Security_Group_Small SHALL appartenir au VPC partagé.
6. THE Security_Group_Medium SHALL autoriser le trafic SSH entrant (port 22) comme règle de base.
7. THE Security_Group_Small SHALL autoriser le trafic SSH entrant (port 22) comme règle de base.

### Requirement 8: Configuration de l'AMI

**User Story:** En tant que développeur, je veux que les instances EC2 utilisent une AMI Debian récente, afin de bénéficier d'un système d'exploitation stable et familier.

#### Acceptance Criteria

1. THE EC2_Instance_Medium SHALL utiliser la dernière AMI Debian disponible dans la région de déploiement.
2. THE EC2_Instance_Small SHALL utiliser la dernière AMI Debian disponible dans la région de déploiement.
