# Document de Requirements — Saga Resilience Improvement

## Introduction

Le système CMV utilise une architecture microservices avec trois services : `cmv_gateway` (API gateway), `cmv_patients` (service patients) et `cmv_chambres` (service chambres). Le flux de suppression d'un patient implique un pattern saga distribué : suppression du patient → suppression des admissions → annulation des réservations de chambres via HTTP.

Le saga actuel présente plusieurs faiblesses : compensations fragiles (print au lieu de logging structuré), deux implémentations divergentes de `delete_admission`, gestion manuelle des commits/rollbacks, et aucun mécanisme de retry pour les compensations HTTP échouées. Cette feature vise à rendre le saga plus résilient et observable.

## Glossaire

- **Saga_Engine** : Module centralisé dans `cmv_patients` responsable de l'orchestration des étapes du saga de suppression (actions et compensations).
- **Outbox_Table** : Table de base de données dans `cmv_patients` stockant les compensations HTTP en attente d'exécution, permettant un retry fiable.
- **Compensation** : Action inverse exécutée pour annuler une étape du saga en cas d'échec (ex : recréer une réservation après une annulation).
- **Service_Patients** : Microservice `cmv_patients` gérant les patients, admissions et documents.
- **Service_Chambres** : Microservice `cmv_chambres` gérant les chambres et réservations.
- **Admission** : Enregistrement d'un séjour patient, pouvant être ambulatoire (sans chambre) ou avec réservation de chambre.
- **Réservation** : Allocation d'une chambre à un patient pour la durée de son admission.
- **Logger_Structuré** : Module de logging Python standard (`logging`) remplaçant les `print()` pour la traçabilité des erreurs de compensation.

## Requirements

### Requirement 1 : Logging structuré des échecs de compensation

**User Story :** En tant qu'opérateur, je veux que les échecs de compensation soient tracés via un logger structuré, afin de pouvoir diagnostiquer les incohérences d'état en production.

#### Critères d'acceptation

1. WHEN une compensation HTTP échoue, THE Saga_Engine SHALL enregistrer l'échec via le Logger_Structuré avec le niveau ERROR, incluant l'identifiant de l'admission, l'identifiant de la réservation, le type de compensation et le message d'erreur.
2. WHEN une compensation HTTP réussit, THE Saga_Engine SHALL enregistrer le succès via le Logger_Structuré avec le niveau INFO, incluant l'identifiant de l'admission et le type de compensation.
3. THE Saga_Engine SHALL ne contenir aucun appel `print()` pour la journalisation des opérations de compensation.

### Requirement 2 : Unification de delete_admission

**User Story :** En tant que développeur, je veux une seule implémentation de `delete_admission` avec compensation, afin d'éviter les divergences de comportement selon le chemin d'appel.

#### Critères d'acceptation

1. THE Service_Patients SHALL exposer une unique fonction `delete_admission` intégrant le tracking des actions et la logique de compensation.
2. WHEN `delete_admission` est appelée depuis `PatientsService.delete_patient`, THE Service_Patients SHALL utiliser la même implémentation que lors d'un appel direct via `AdmissionService`.
3. WHEN une admission non-ambulatoire avec réservation est supprimée, THE Service_Patients SHALL annuler la réservation associée via un appel HTTP au Service_Chambres avant de supprimer l'admission en base.
4. IF l'annulation de la réservation échoue, THEN THE Service_Patients SHALL effectuer un rollback de la session de base de données et remonter une erreur HTTP 400.

### Requirement 3 : Table outbox pour les compensations échouées

**User Story :** En tant qu'opérateur, je veux que les compensations HTTP échouées soient persistées dans une table outbox, afin qu'elles puissent être rejouées ultérieurement et éviter les états incohérents.

#### Critères d'acceptation

1. THE Service_Patients SHALL disposer d'une Outbox_Table contenant les colonnes : identifiant, type de compensation, payload JSON, nombre de tentatives, statut (pending, completed, failed), date de création et date de dernière tentative.
2. WHEN une compensation HTTP échoue, THE Saga_Engine SHALL insérer un enregistrement dans la Outbox_Table avec le statut "pending" et le payload nécessaire pour rejouer la compensation.
3. WHEN le processus de retry s'exécute, THE Saga_Engine SHALL tenter de rejouer chaque compensation "pending" dont le nombre de tentatives est inférieur à un seuil configurable.
4. WHEN une compensation rejouée réussit, THE Saga_Engine SHALL mettre à jour le statut de l'enregistrement à "completed" dans la Outbox_Table.
5. WHEN une compensation rejouée échoue et que le nombre de tentatives atteint le seuil configurable, THE Saga_Engine SHALL mettre à jour le statut à "failed" et enregistrer l'échec via le Logger_Structuré avec le niveau CRITICAL.
6. IF le Service_Chambres est indisponible lors d'une compensation, THEN THE Saga_Engine SHALL incrémenter le compteur de tentatives et conserver le statut "pending" dans la Outbox_Table.

### Requirement 4 : Gestion transactionnelle cohérente du saga

**User Story :** En tant que développeur, je veux que la gestion des transactions de base de données soit cohérente dans le saga, afin d'éviter les états partiels entre le commit et le return.

#### Critères d'acceptation

1. THE Saga_Engine SHALL effectuer le `db.commit()` uniquement après que toutes les étapes locales du saga (suppression admission, insertion outbox si nécessaire) soient terminées avec succès.
2. IF une exception survient pendant une étape locale du saga, THEN THE Saga_Engine SHALL effectuer un `db.rollback()` complet couvrant toutes les modifications locales.
3. WHEN le saga de suppression d'admission s'exécute, THE Saga_Engine SHALL regrouper la suppression de l'admission et l'éventuelle insertion outbox dans une seule transaction de base de données.

### Requirement 5 : Transmission des headers d'authentification dans les compensations

**User Story :** En tant que développeur, je veux que les compensations HTTP transmettent les headers d'authentification, afin que le Service_Chambres puisse valider les appels de compensation.

#### Critères d'acceptation

1. WHEN le Saga_Engine exécute une compensation HTTP vers le Service_Chambres, THE Saga_Engine SHALL inclure les headers Authorization, X-Real-IP et X-Forwarded-For dans la requête.
2. WHEN une compensation est rejouée depuis la Outbox_Table, THE Saga_Engine SHALL utiliser un token de service interne pour l'authentification, le token utilisateur original pouvant avoir expiré.
