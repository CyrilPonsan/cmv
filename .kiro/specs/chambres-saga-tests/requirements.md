# Document d'exigences — Tests Saga côté Chambres (participant)

## Introduction

Ce document définit les exigences pour la couverture de tests du côté participant de la Saga dans le microservice chambres (`cmv_chambres`). Le service chambres reçoit des requêtes HTTP du service admissions (orchestrateur) pour réserver et annuler des chambres. Les tests doivent valider le comportement des endpoints de réservation (`POST /{service_id}/reserver`) et d'annulation (`DELETE /{reservation_id}/{chambre_id}/cancel`), ainsi que la logique métier interne de `ChambresService` : disponibilité des chambres, création de réservations, mise à jour des statuts et annulation.

## Glossaire

- **ChambresService** : Service métier gérant la logique de réservation et d'annulation de chambres dans le microservice `cmv_chambres`
- **PgChambresRepository** : Couche d'accès aux données pour les opérations CRUD sur les chambres et réservations
- **Chambre** : Entité représentant une chambre d'hôpital, avec un statut (LIBRE, OCCUPEE, NETTOYAGE) et un rattachement à un Service
- **Reservation** : Entité représentant une réservation de chambre, liée à une Chambre et référençant un patient via `ref`
- **Service_Hospitalier** : Entité représentant un service hospitalier (ex. Cardiologie, Neurologie) contenant des chambres
- **Status** : Énumération des états possibles d'une chambre : `LIBRE`, `OCCUPEE`, `NETTOYAGE`
- **CreateReservation** : Schéma Pydantic d'entrée pour créer une réservation (`patient_id`, `entree_prevue`, `sortie_prevue`)
- **ReservationResponse** : Schéma Pydantic de réponse contenant `reservation_id`, `chambre_id` et `sortie_prevue_le`
- **Orchestrateur** : Le service admissions (`cmv_patients`) qui émet les requêtes HTTP de réservation et d'annulation vers le service chambres

## Exigences

### Exigence 1 : Réservation de chambre — chemin nominal

**User Story :** En tant que développeur, je veux vérifier que la réservation d'une chambre fonctionne correctement lorsqu'une chambre est disponible, afin de garantir que le participant Saga répond correctement à l'orchestrateur.

#### Critères d'acceptation

1. WHEN une requête POST `/{service_id}/reserver` est reçue avec des données CreateReservation valides et qu'une Chambre avec le statut LIBRE existe dans le Service_Hospitalier demandé, THE ChambresService SHALL créer une Reservation en base de données avec les champs `chambre_id`, `ref`, `entree_prevue` et `sortie_prevue` correspondant aux données soumises
2. WHEN une réservation est créée avec succès, THE ChambresService SHALL mettre à jour le statut de la Chambre réservée de LIBRE à OCCUPEE
3. WHEN une réservation est créée avec succès, THE ChambresService SHALL retourner une ReservationResponse avec le `reservation_id`, le `chambre_id` et la `sortie_prevue_le` de la réservation créée, avec un code HTTP 201

### Exigence 2 : Réservation de chambre — aucune chambre disponible

**User Story :** En tant que développeur, je veux vérifier que la réservation échoue proprement lorsqu'aucune chambre n'est disponible, afin que l'orchestrateur puisse gérer ce cas d'erreur.

#### Critères d'acceptation

1. WHEN une requête POST `/{service_id}/reserver` est reçue et qu'aucune Chambre avec le statut LIBRE n'existe dans le Service_Hospitalier demandé, THE ChambresService SHALL lever une HTTPException avec le statut 404 et le détail `no_room_available`
2. WHEN aucune chambre n'est disponible, THE ChambresService SHALL ne créer aucune Reservation en base de données
3. WHEN aucune chambre n'est disponible, THE ChambresService SHALL ne modifier le statut d'aucune Chambre

### Exigence 3 : Réservation de chambre — service inexistant

**User Story :** En tant que développeur, je veux vérifier que la réservation échoue lorsque le service hospitalier demandé n'existe pas, afin de garantir une gestion correcte des identifiants invalides.

#### Critères d'acceptation

1. WHEN une requête POST `/{service_id}/reserver` est reçue avec un `service_id` ne correspondant à aucun Service_Hospitalier, THE ChambresService SHALL lever une HTTPException avec le statut 404 et le détail `no_room_available`
2. WHEN le service demandé n'existe pas, THE ChambresService SHALL ne créer aucune Reservation en base de données

### Exigence 4 : Annulation de réservation — chemin nominal

**User Story :** En tant que développeur, je veux vérifier que l'annulation d'une réservation libère la chambre et supprime la réservation, afin de garantir que la compensation Saga fonctionne côté participant.

#### Critères d'acceptation

1. WHEN une requête DELETE `/{reservation_id}/{chambre_id}/cancel` est reçue avec un `reservation_id` et un `chambre_id` valides, THE ChambresService SHALL supprimer la Reservation de la base de données
2. WHEN une annulation est effectuée avec succès, THE ChambresService SHALL mettre à jour le statut de la Chambre de OCCUPEE à LIBRE
3. WHEN une annulation est effectuée avec succès, THE ChambresService SHALL retourner un code HTTP 200

### Exigence 5 : Annulation de réservation — chambre introuvable

**User Story :** En tant que développeur, je veux vérifier que l'annulation échoue proprement lorsque la chambre référencée n'existe pas, afin de garantir une gestion correcte des cas d'erreur.

#### Critères d'acceptation

1. WHEN une requête DELETE `/{reservation_id}/{chambre_id}/cancel` est reçue avec un `chambre_id` ne correspondant à aucune Chambre, THE ChambresService SHALL lever une HTTPException avec le statut 404 et le détail `chambre_not_found`
2. WHEN la chambre n'existe pas, THE ChambresService SHALL ne supprimer aucune Reservation de la base de données

### Exigence 6 : Annulation de réservation — réservation introuvable

**User Story :** En tant que développeur, je veux vérifier que l'annulation échoue proprement lorsque la réservation référencée n'existe pas, afin de garantir une gestion correcte des identifiants invalides.

#### Critères d'acceptation

1. WHEN une requête DELETE `/{reservation_id}/{chambre_id}/cancel` est reçue avec un `reservation_id` ne correspondant à aucune Reservation mais un `chambre_id` valide, THE ChambresService SHALL lever une HTTPException avec le statut 404 et le détail `reservation_not_found`
2. WHEN la réservation n'existe pas mais la chambre existe, THE ChambresService SHALL tout de même mettre à jour le statut de la Chambre à LIBRE avant de lever l'erreur

### Exigence 7 : Cohérence statut chambre et réservation (round-trip)

**User Story :** En tant que développeur, je veux vérifier que le cycle réservation puis annulation ramène la chambre à son état initial, afin de garantir la cohérence transactionnelle du participant Saga.

#### Critères d'acceptation

1. FOR ALL CreateReservation valides avec un Service_Hospitalier contenant une Chambre LIBRE, réserver puis annuler SHALL remettre le statut de la Chambre à LIBRE
2. FOR ALL CreateReservation valides avec un Service_Hospitalier contenant une Chambre LIBRE, réserver puis annuler SHALL supprimer la Reservation de la base de données
3. FOR ALL CreateReservation valides avec un Service_Hospitalier contenant une Chambre LIBRE, après le cycle réservation-annulation, le nombre total de Reservations en base SHALL être identique au nombre initial

### Exigence 8 : Disponibilité des chambres — sélection correcte

**User Story :** En tant que développeur, je veux vérifier que seules les chambres avec le statut LIBRE sont retournées comme disponibles, afin de garantir qu'aucune chambre occupée ou en nettoyage ne soit réservée.

#### Critères d'acceptation

1. WHEN une chambre disponible est recherchée, THE ChambresService SHALL retourner uniquement une Chambre avec le statut LIBRE appartenant au Service_Hospitalier demandé
2. WHILE toutes les Chambres d'un Service_Hospitalier ont le statut OCCUPEE ou NETTOYAGE, THE ChambresService SHALL lever une HTTPException avec le statut 404 et le détail `no_room_available`
3. WHEN plusieurs Chambres LIBRE existent dans un Service_Hospitalier, THE ChambresService SHALL retourner une seule Chambre

### Exigence 9 : Validation des données de réservation

**User Story :** En tant que développeur, je veux vérifier que les données de réservation invalides sont rejetées par la validation Pydantic, afin de garantir l'intégrité des données entrantes.

#### Critères d'acceptation

1. WHEN une requête POST `/{service_id}/reserver` est reçue avec un body ne contenant pas les champs requis (`patient_id`, `entree_prevue`, `sortie_prevue`), THE ChambresService SHALL retourner un code HTTP 422 avec les détails de validation
2. WHEN une requête POST `/{service_id}/reserver` est reçue avec des types de données invalides pour les champs datetime, THE ChambresService SHALL retourner un code HTTP 422

### Exigence 10 : Authentification des endpoints de réservation et d'annulation

**User Story :** En tant que développeur, je veux vérifier que les endpoints de réservation sont protégés par authentification JWT, afin de garantir que seuls les services autorisés peuvent réserver ou annuler des chambres.

#### Critères d'acceptation

1. WHEN une requête POST `/{service_id}/reserver` est reçue sans token JWT, THE ChambresService SHALL retourner un code HTTP 401 avec le détail `Not authenticated`
2. WHEN une requête POST `/{service_id}/reserver` est reçue avec un token JWT invalide, THE ChambresService SHALL retourner un code HTTP 403 avec le détail `not_authorized`
3. WHEN une requête POST `/{service_id}/reserver` est reçue avec un token JWT valide dont la source est `api_patients` ou `api_gateway`, THE ChambresService SHALL autoriser la requête
