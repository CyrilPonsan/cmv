# Requirements Document

## Introduction

Ce document définit les exigences pour créer un script AWS CDK en TypeScript permettant de déployer une infrastructure distribuée pour l'application CMV. L'objectif est de remplacer le déploiement sur une instance unique par une architecture multi-instances avec une instance EC2 dédiée par service.

## Glossary

- **CDK_Stack**: La pile AWS CDK qui orchestre le déploiement de l'infrastructure
- **Service_Instance**: Une instance EC2 dédiée à un microservice spécifique
- **Database_Instance**: Une instance EC2 configurée avec PostgreSQL
- **Admin_Role**: Rôle PostgreSQL avec tous les privilèges sur la base de données
- **CRUD_Role**: Rôle PostgreSQL avec privilèges limités (Create, Read, Update, Delete)
- **Security_Group**: Groupe de sécurité AWS définissant les règles de trafic réseau
- **VPC**: Virtual Private Cloud isolant l'infrastructure réseau

## Requirements

### Requirement 1

**User Story:** En tant que développeur, je veux déployer plusieurs instances EC2 à partir d'une configuration tableau, afin de pouvoir facilement ajouter ou modifier des services.

#### Acceptance Criteria

1. WHEN the CDK_Stack is deployed THEN the system SHALL create EC2 instances based on a TypeScript array configuration
2. WHEN a service configuration is added to the array THEN the system SHALL deploy a new Service_Instance automatically
3. WHEN instance properties are modified in the array THEN the system SHALL update the corresponding Service_Instance
4. WHERE an instance requires PostgreSQL THEN the system SHALL install and configure PostgreSQL on that Service_Instance
5. WHEN the deployment completes THEN the system SHALL output connection details for each Service_Instance

### Requirement 2

**User Story:** En tant qu'administrateur système, je veux que chaque instance soit déployée sur Debian t2.micro dans le même VPC, afin d'assurer la cohérence et la sécurité.

#### Acceptance Criteria

1. THE CDK_Stack SHALL deploy all Service_Instance using t2.micro instance type
2. THE CDK_Stack SHALL use Debian as the operating system for all Service_Instance
3. WHEN instances are created THEN the system SHALL place all Service_Instance in the same VPC
4. WHEN the VPC is created THEN the system SHALL configure appropriate subnets for the Service_Instance
5. THE CDK_Stack SHALL apply the same Security_Group rules to all Service_Instance initially

### Requirement 3

**User Story:** En tant que développeur, je veux configurer PostgreSQL avec des rôles admin et CRUD à partir de variables d'environnement, afin de sécuriser l'accès aux bases de données.

#### Acceptance Criteria

1. WHEN PostgreSQL is installed on a Database_Instance THEN the system SHALL create an Admin_Role with full privileges
2. WHEN PostgreSQL is configured THEN the system SHALL create a CRUD_Role with limited privileges (SELECT, INSERT, UPDATE, DELETE)
3. WHEN database roles are created THEN the system SHALL use environment variables for credentials configuration
4. THE system SHALL prevent the Admin_Role credentials from being exposed in logs or outputs
5. WHEN the CRUD_Role is created THEN the system SHALL restrict privileges to data manipulation only (no schema changes)

### Requirement 4

**User Story:** En tant qu'ingénieur DevOps, je veux que le script soit évolutif et maintenable, afin de pouvoir facilement adapter l'infrastructure aux besoins futurs.

#### Acceptance Criteria

1. THE CDK_Stack SHALL use TypeScript interfaces to define service configuration structure
2. WHEN new service types are needed THEN the system SHALL allow extension through interface inheritance
3. THE CDK_Stack SHALL separate infrastructure concerns into reusable constructs
4. WHEN the script is executed THEN the system SHALL validate configuration before deployment
5. THE system SHALL provide clear error messages for invalid configurations

### Requirement 5

**User Story:** En tant que développeur, je veux que les instances puissent communiquer entre elles de manière sécurisée, afin de maintenir l'architecture microservices.

#### Acceptance Criteria

1. WHEN Security_Group rules are applied THEN the system SHALL allow inter-instance communication within the VPC
2. THE system SHALL block external access to Database_Instance by default
3. WHEN a gateway service is deployed THEN the system SHALL allow HTTP/HTTPS traffic from the internet
4. THE system SHALL allow SSH access for administration purposes with key-based authentication
5. WHEN database services are deployed THEN the system SHALL allow PostgreSQL connections only from authorized Service_Instance