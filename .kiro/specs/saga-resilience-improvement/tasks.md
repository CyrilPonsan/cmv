# Plan d'implémentation : Saga Resilience Improvement

## Vue d'ensemble

Refactorisation du pattern saga distribué dans `cmv_patients` pour améliorer la résilience du flux de suppression admission/patient. L'implémentation suit un ordre incrémental : modèle outbox → repository outbox → SagaEngine → refactorisation AdmissionService → refactorisation PatientsService → migration Alembic → endpoint retry → tests.

## Tâches

- [x] 1. Créer le modèle OutboxEntry et le repository outbox
  - [x] 1.1 Ajouter le modèle `OutboxEntry` et l'enum `OutboxStatus` dans `cmv_patients/app/sql/models.py`
    - Ajouter l'enum `OutboxStatus` (PENDING, COMPLETED, FAILED)
    - Ajouter la classe `OutboxEntry` avec les colonnes : id, compensation_type, payload (JSON), retry_count, status, created_at, last_attempted_at
    - _Requirements: 3.1_

  - [x] 1.2 Créer le repository `PgOutboxRepository` dans `cmv_patients/app/repositories/outbox_crud.py`
    - Implémenter `create_entry(db, entry) -> OutboxEntry`
    - Implémenter `get_pending_entries(db, max_retries) -> list[OutboxEntry]` (filtre status=PENDING et retry_count < max_retries)
    - Implémenter `update_status(db, entry_id, status, increment_retries)` avec mise à jour de `last_attempted_at`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 1.3 Écrire les tests unitaires pour PgOutboxRepository
    - Tester la création d'une entrée outbox
    - Tester le filtrage des entrées pending par retry_count
    - Tester la mise à jour de statut et l'incrémentation du retry_count
    - _Requirements: 3.1_

- [x] 2. Implémenter le SagaEngine
  - [x] 2.1 Créer le module `SagaEngine` dans `cmv_patients/app/services/saga_engine.py`
    - Implémenter le constructeur avec injection de `PgAdmissionsRepository`, `PgOutboxRepository`, `logging.Logger`, `httpx.AsyncClient`
    - Implémenter `execute_delete_admission(db, admission, headers)` : orchestre annulation réservation → suppression admission → commit atomique
    - Implémenter `_cancel_reservation(db, admission, headers)` : appel HTTP DELETE, insertion outbox si échec
    - Utiliser `logging.Logger` (pas de `print()`) pour toute la journalisation
    - _Requirements: 1.1, 1.2, 1.3, 2.3, 2.4, 3.2, 4.1, 4.2, 4.3, 5.1_

  - [x] 2.2 Écrire le test property-based pour le logging structuré
    - **Property 1 : Logging structuré des compensations**
    - **Validates: Requirements 1.1, 1.2**

  - [x] 2.3 Écrire le test property-based pour l'annulation avant suppression
    - **Property 2 : Annulation de réservation avant suppression**
    - **Validates: Requirements 2.3**

  - [x] 2.4 Écrire le test property-based pour le rollback sur échec
    - **Property 3 : Rollback sur échec d'annulation**
    - **Validates: Requirements 2.4**

  - [x] 2.5 Écrire le test property-based pour l'insertion outbox
    - **Property 4 : Insertion outbox sur échec de compensation**
    - **Validates: Requirements 3.2, 3.6**

  - [x] 2.6 Écrire le test property-based pour la transaction atomique
    - **Property 7 : Transaction atomique du saga**
    - **Validates: Requirements 4.1, 4.3**

  - [x] 2.7 Écrire le test property-based pour le rollback complet
    - **Property 8 : Rollback complet sur exception**
    - **Validates: Requirements 4.2**

  - [x] 2.8 Écrire le test property-based pour les headers d'authentification
    - **Property 9 : Transmission des headers d'authentification**
    - **Validates: Requirements 5.1**

- [x] 3. Checkpoint - Vérifier le SagaEngine
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implémenter le retry outbox dans le SagaEngine
  - [x] 4.1 Ajouter la méthode `retry_pending_compensations(db, max_retries)` au SagaEngine
    - Récupérer les entrées pending via `PgOutboxRepository.get_pending_entries`
    - Pour chaque entrée : tenter la compensation HTTP, mettre à jour le statut (completed/pending/failed)
    - Utiliser un token de service interne pour le header Authorization
    - Logger CRITICAL si le seuil de retry est atteint
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 5.2_

  - [x] 4.2 Écrire le test property-based pour le cycle de vie du retry
    - **Property 5 : Cycle de vie du retry outbox**
    - **Validates: Requirements 3.3, 3.4, 3.6**

  - [x] 4.3 Écrire le test property-based pour le seuil de retry
    - **Property 6 : Seuil de retry atteint**
    - **Validates: Requirements 3.5**

  - [x] 4.4 Écrire le test property-based pour le token de service
    - **Property 10 : Token de service pour les retries outbox**
    - **Validates: Requirements 5.2**

- [x] 5. Refactoriser AdmissionService et PatientsService
  - [x] 5.1 Refactoriser `AdmissionService.delete_admission` dans `cmv_patients/app/services/admissions.py`
    - Supprimer la logique de compensation inline
    - Déléguer au `SagaEngine.execute_delete_admission`
    - Construire les headers (Authorization, X-Real-IP, X-Forwarded-For) depuis la requête
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1_

  - [x] 5.2 Refactoriser `PatientsService.delete_admission` dans `cmv_patients/app/services/patients.py`
    - Supprimer l'implémentation dupliquée de `delete_admission`
    - `delete_patient` doit appeler `AdmissionService.delete_admission` pour chaque admission
    - _Requirements: 2.1, 2.2_

  - [x] 5.3 Écrire les tests unitaires pour la délégation
    - Vérifier que `PatientsService.delete_patient` appelle `AdmissionService.delete_admission`
    - Vérifier qu'aucun `print()` n'existe dans le SagaEngine
    - Edge case : admission ambulatoire sans réservation → pas d'appel HTTP
    - Edge case : admission inexistante → HTTPException 404
    - _Requirements: 2.1, 2.2, 1.3_

- [x] 6. Créer la migration Alembic et l'endpoint retry
  - [x] 6.1 Générer la migration Alembic pour la table `outbox`
    - Créer la migration dans `cmv_patients/alembic/versions/`
    - La table doit correspondre au modèle `OutboxEntry`
    - _Requirements: 3.1_

  - [x] 6.2 Créer l'endpoint `/admin/outbox/retry` dans `cmv_patients/app/routers/`
    - Endpoint POST protégé par authentification
    - Appelle `SagaEngine.retry_pending_compensations`
    - Retourne un résumé des compensations rejouées (succès/échecs)
    - _Requirements: 3.3_

- [x] 7. Checkpoint final - Validation complète
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées `*` sont optionnelles et peuvent être ignorées pour un MVP plus rapide
- Chaque tâche référence les requirements spécifiques pour la traçabilité
- Les checkpoints permettent une validation incrémentale
- Les tests property-based utilisent Hypothesis (déjà configuré dans le projet)
- Les tests unitaires valident les cas spécifiques et les edge cases
