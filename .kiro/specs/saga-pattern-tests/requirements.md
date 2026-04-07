# Document d'exigences — Tests du pattern Saga

## Introduction

Ce document définit les exigences pour la couverture de tests du pattern Saga implémenté dans le service d'admissions (`cmv_patients`). Le pattern Saga orchestre la création d'admissions en coordonnant un appel HTTP vers le service chambres (réservation) et une écriture en base de données, avec un mécanisme de compensation en cas d'échec. Les tests doivent valider le bon fonctionnement du happy path, la gestion des erreurs et le mécanisme de compensation (rollback) pour `create_admission()` et `delete_admission()`.

## Glossaire

- **AdmissionService** : Service métier orchestrant la création et la suppression d'admissions via le pattern Saga
- **Saga** : Pattern de coordination de transactions distribuées avec mécanisme de compensation
- **Compensation** : Action d'annulation (rollback) exécutée lorsqu'une étape de la saga échoue après qu'une étape précédente a réussi
- **Service_Chambres** : Microservice externe géré via des appels HTTP (httpx) pour la réservation et l'annulation de chambres
- **Réservation** : Ressource créée dans le Service_Chambres lors d'une admission non ambulatoire, identifiée par `reservation_id` et `chambre_id`
- **Admission_Ambulatoire** : Admission ne nécessitant pas de réservation de chambre (`ambulatoire=True`)
- **Admission_Hospitalisation** : Admission nécessitant une réservation de chambre (`ambulatoire=False`, `service_id` requis)
- **Repository** : Couche d'accès aux données (PgAdmissionsRepository) pour les opérations CRUD sur les admissions

## Exigences

### Exigence 1 : Création d'admission ambulatoire (happy path)

**User Story :** En tant que développeur, je veux vérifier que la création d'une admission ambulatoire fonctionne sans appel au Service_Chambres, afin de garantir que le chemin nominal sans réservation est correct.

#### Critères d'acceptation

1. WHEN une CreateAdmission avec `ambulatoire=True` est soumise, THE AdmissionService SHALL créer une Admission en base de données sans appeler le Service_Chambres
2. WHEN une admission ambulatoire est créée avec succès, THE AdmissionService SHALL retourner une Admission avec `ref_reservation` égal à `None`
3. WHEN une admission ambulatoire est créée avec succès, THE AdmissionService SHALL persister l'Admission avec les champs `patient_id`, `entree_le`, `sortie_prevue_le` et `ambulatoire` correspondant aux données soumises

### Exigence 2 : Création d'admission non ambulatoire avec réservation (happy path)

**User Story :** En tant que développeur, je veux vérifier que la création d'une admission non ambulatoire réserve une chambre puis crée l'admission, afin de garantir que la saga complète fonctionne correctement.

#### Critères d'acceptation

1. WHEN une CreateAdmission avec `ambulatoire=False` et un `service_id` valide est soumise, THE AdmissionService SHALL appeler le Service_Chambres via POST pour réserver une chambre
2. WHEN le Service_Chambres retourne un statut 201 avec `reservation_id` et `chambre_id`, THE AdmissionService SHALL créer une Admission en base avec `ref_reservation` égal au `reservation_id` retourné
3. WHEN la réservation et la création en base réussissent, THE AdmissionService SHALL retourner l'Admission complète avec la référence de réservation

### Exigence 3 : Échec de la réservation de chambre

**User Story :** En tant que développeur, je veux vérifier que l'échec de la réservation empêche la création de l'admission, afin de garantir la cohérence transactionnelle.

#### Critères d'acceptation

1. WHEN le Service_Chambres retourne un statut 404, THE AdmissionService SHALL lever une HTTPException avec le statut 404 et le détail `no_room_available`
2. WHEN le Service_Chambres retourne un statut 500, THE AdmissionService SHALL lever une HTTPException avec le statut 500 et le détail `reservation_failed`
3. WHEN la réservation échoue, THE AdmissionService SHALL ne créer aucune Admission en base de données

### Exigence 4 : Compensation — Annulation de la réservation après échec de la création en base

**User Story :** En tant que développeur, je veux vérifier que la compensation annule la réservation lorsque la création de l'admission en base échoue, afin de garantir qu'aucune réservation orpheline ne subsiste.

#### Critères d'acceptation

1. WHEN la réservation réussit mais la création en base échoue avec une Exception, THE AdmissionService SHALL appeler le Service_Chambres via DELETE pour annuler la réservation
2. WHEN la compensation est déclenchée, THE AdmissionService SHALL envoyer la requête DELETE avec le `reservation_id` et le `chambre_id` de la réservation créée
3. WHEN la réservation réussit mais la création en base échoue avec une HTTPException, THE AdmissionService SHALL appeler la compensation puis relever la même HTTPException

### Exigence 5 : Échec de la compensation elle-même

**User Story :** En tant que développeur, je veux vérifier que l'échec de la compensation est géré gracieusement sans masquer l'erreur originale, afin de garantir la résilience du système.

#### Critères d'acceptation

1. WHEN la compensation échoue (exception lors de l'appel DELETE), THE AdmissionService SHALL capturer l'exception de compensation sans la propager
2. WHEN la compensation échoue, THE AdmissionService SHALL propager l'erreur originale (celle qui a déclenché la compensation) au code appelant
3. WHEN la compensation échoue, THE AdmissionService SHALL journaliser l'échec de compensation via un print

### Exigence 6 : Suppression d'admission avec annulation de réservation (happy path)

**User Story :** En tant que développeur, je veux vérifier que la suppression d'une admission non ambulatoire annule la réservation puis supprime l'admission, afin de garantir le bon fonctionnement de la saga inverse.

#### Critères d'acceptation

1. WHEN une suppression est demandée pour une admission non ambulatoire avec `ref_reservation`, THE AdmissionService SHALL appeler le Service_Chambres via DELETE pour annuler la réservation
2. WHEN l'annulation de la réservation réussit (statut 200 ou 404), THE AdmissionService SHALL supprimer l'Admission de la base de données
3. WHEN la suppression complète réussit, THE AdmissionService SHALL retourner `{"message": "admission_deleted"}`

### Exigence 7 : Suppression d'admission ambulatoire

**User Story :** En tant que développeur, je veux vérifier que la suppression d'une admission ambulatoire fonctionne sans appel au Service_Chambres, afin de garantir le chemin nominal sans annulation de réservation.

#### Critères d'acceptation

1. WHEN une suppression est demandée pour une admission ambulatoire, THE AdmissionService SHALL supprimer l'Admission sans appeler le Service_Chambres
2. WHEN la suppression d'une admission ambulatoire réussit, THE AdmissionService SHALL retourner `{"message": "admission_deleted"}`

### Exigence 8 : Échec de l'annulation de réservation lors de la suppression

**User Story :** En tant que développeur, je veux vérifier que l'échec de l'annulation de réservation empêche la suppression de l'admission, afin de garantir la cohérence transactionnelle.

#### Critères d'acceptation

1. WHEN l'annulation de la réservation retourne un statut autre que 200 ou 404, THE AdmissionService SHALL lever une HTTPException avec le statut 400 et le détail `failed_to_cancel_reservation`
2. WHEN l'annulation de la réservation échoue, THE AdmissionService SHALL effectuer un rollback de la session de base de données
3. WHEN l'annulation de la réservation échoue, THE AdmissionService SHALL ne pas supprimer l'Admission de la base de données

### Exigence 9 : Suppression d'une admission inexistante

**User Story :** En tant que développeur, je veux vérifier que la suppression d'une admission inexistante retourne une erreur 404, afin de garantir une gestion correcte des cas limites.

#### Critères d'acceptation

1. WHEN une suppression est demandée pour un `admission_id` inexistant, THE AdmissionService SHALL lever une HTTPException avec le statut 404 et le détail `admission_not_found`
