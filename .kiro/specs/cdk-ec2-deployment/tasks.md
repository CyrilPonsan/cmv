# Implementation Plan: CDK EC2 Deployment

## Overview

Implémentation incrémentale du projet AWS CDK TypeScript dans `cdk/`. On commence par le scaffolding du projet et la configuration, puis les ressources de la stack (VPC, KMS, Security Groups, EC2), et enfin les tests unitaires et property-based.

## Tasks

- [x] 1. Scaffolding du projet CDK et configuration
  - [x] 1.1 Créer les fichiers de configuration du projet CDK
    - Créer `cdk/package.json` avec les dépendances : `aws-cdk-lib`, `constructs`, `dotenv`, et dev deps : `typescript`, `ts-node`, `jest`, `ts-jest`, `@types/jest`, `fast-check`
    - Créer `cdk/tsconfig.json` avec la configuration TypeScript pour CDK
    - Créer `cdk/cdk.json` avec le point d'entrée `npx ts-node --prefer-ts-exts bin/cdk-app.ts`
    - _Requirements: 1.3_

  - [x] 1.2 Créer le point d'entrée CDK (`cdk/bin/cdk-app.ts`)
    - Charger les variables d'environnement depuis `cdk/.env` via `dotenv.config()`
    - Valider la présence des variables obligatoires (`CDK_DEFAULT_ACCOUNT`, `CDK_DEFAULT_REGION`, `DOMAIN`) avec erreur explicite si absente
    - Instancier `cdk.App` et `CdkEc2Stack` avec `env: { account, region }`
    - _Requirements: 1.2, 2.1, 2.3, 2.4_

  - [x] 1.3 Créer le squelette de la stack (`cdk/lib/cdk-ec2-stack.ts`)
    - Créer la classe `CdkEc2Stack` étendant `cdk.Stack` avec un constructeur vide (les ressources seront ajoutées dans les tâches suivantes)
    - _Requirements: 1.1_

- [x] 2. Implémenter les ressources de la stack
  - [x] 2.1 Ajouter le VPC partagé
    - Créer un `ec2.Vpc` avec `maxAzs: 2` et au moins un sous-réseau public
    - _Requirements: 3.1, 3.2_

  - [x] 2.2 Ajouter la clé KMS
    - Créer un `kms.Key` avec `enableKeyRotation: true`
    - _Requirements: 4.1_

  - [x] 2.3 Ajouter les deux Security Groups
    - Créer `Security_Group_Medium` et `Security_Group_Small` dans le VPC partagé
    - Ajouter une règle SSH entrante (port 22) sur chaque security group
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [x] 2.4 Ajouter l'instance EC2 T2.medium
    - Créer une `ec2.Instance` de type `t2.medium` avec AMI Debian
    - Configurer un volume EBS de 30 Go chiffré avec la clé KMS (GP3, `/dev/xvda`)
    - Associer au `Security_Group_Medium` et au VPC partagé
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.1_

  - [x] 2.5 Ajouter l'instance EC2 T3.small
    - Créer une `ec2.Instance` de type `t3.small` avec AMI Debian
    - Configurer un volume EBS de 30 Go chiffré avec la clé KMS (GP3, `/dev/xvda`)
    - Associer au `Security_Group_Small` et au VPC partagé
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 8.2_

- [x] 3. Checkpoint - Vérifier la synthèse CDK
  - Ensure all tests pass, ask the user if questions arise.
  - Exécuter `npx cdk synth` dans `cdk/` pour vérifier que le template CloudFormation est généré sans erreur

- [x] 4. Tests unitaires et property-based
  - [x] 4.1 Configurer Jest pour le projet CDK
    - Créer `cdk/jest.config.js` avec la configuration `ts-jest` pour transformer les fichiers TypeScript
    - _Requirements: 1.3_

  - [x] 4.2 Écrire les tests unitaires CDK Assertions (`cdk/test/cdk-ec2-stack.test.ts`)
    - Tester la présence d'une instance `t2.medium` dans le template
    - Tester la présence d'une instance `t3.small` dans le template
    - Tester que chaque volume EBS fait 30 Go
    - Tester que les security groups autorisent SSH (port 22)
    - Tester la présence de la clé KMS
    - Tester la présence du VPC
    - _Requirements: 3.1, 4.1, 5.1, 5.3, 6.1, 6.3, 7.6, 7.7_

  - [x] 4.3 Write property test: Stack environment propagation
    - **Property 1: Stack environment propagation**
    - Générer des paires aléatoires (account, region) via fast-check, synthétiser la stack, vérifier que le template porte les bonnes valeurs
    - **Validates: Requirements 1.2**

  - [x] 4.4 Write property test: Required variable validation
    - **Property 2: Required variable validation**
    - Pour chaque sous-ensemble de variables obligatoires manquantes (généré aléatoirement), vérifier qu'une erreur est levée nommant la variable absente
    - **Validates: Requirements 2.4**

  - [~] 4.5 Write property test: VPC structure invariant
    - **Property 3: VPC structure invariant**
    - Synthétiser la stack avec des configurations valides variées, vérifier la présence du VPC, du sous-réseau public, et que les deux instances le référencent
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [~] 4.6 Write property test: KMS encryption invariant
    - **Property 4: KMS encryption invariant**
    - Synthétiser la stack, vérifier que la clé KMS existe et que les deux volumes EBS la référencent
    - **Validates: Requirements 4.1, 4.2**

  - [~] 4.7 Write property test: Security groups invariant
    - **Property 5: Security groups invariant**
    - Synthétiser la stack, vérifier deux SGs distincts dans le VPC, chacun associé à son instance
    - **Validates: Requirements 7.3, 7.4, 7.5**

- [x] 5. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using fast-check (min 100 iterations)
- Unit tests validate specific examples via CDK Assertions
- All code is TypeScript, executed in the `cdk/` directory
