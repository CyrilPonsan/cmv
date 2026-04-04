# Plan d'implémentation : Tests du pattern Saga

## Vue d'ensemble

Implémentation des tests unitaires et property-based pour le pattern Saga du service d'admissions (`AdmissionService`). Tous les tests sont regroupés dans un fichier unique `cmv_patients/app/tests/test_admissions_saga.py`, utilisant pytest-asyncio, pytest-httpx, pytest-mock et Hypothesis.

## Tâches

- [x] 1. Créer le fichier de test avec les imports, fixtures et générateurs Hypothesis
  - Créer `cmv_patients/app/tests/test_admissions_saga.py`
  - Ajouter les imports : `pytest`, `pytest-asyncio`, `httpx`, `hypothesis`, `unittest.mock`, `AdmissionService`, `PgAdmissionsRepository`, `CreateAdmission`, `Admission`, `Patient`, `CHAMBRES_SERVICE`
  - Implémenter les fixtures `admission_service`, `mock_request`, `patient_in_db`
  - Définir les stratégies Hypothesis : `ambulatoire_admission`, `non_ambulatoire_admission`, `error_status_codes`, `cancel_failure_codes`, `reservation_ids`, `chambre_ids`
  - _Exigences : toutes (1–9)_

- [x] 2. Implémenter les tests de création d'admission (happy path et erreurs)
  - [x] 2.1 Implémenter les tests unitaires de création
    - `test_reservation_404_raises_no_room_available` : vérifier HTTPException 404 avec détail `no_room_available` quand le Service_Chambres retourne 404
    - `test_reservation_500_raises_reservation_failed` : vérifier HTTPException 500 avec détail `reservation_failed` quand le Service_Chambres retourne 500
    - _Exigences : 3.1, 3.2_

  - [x] 2.2 Écrire le test property-based pour l'admission ambulatoire (round-trip)
    - **Propriété 1 : Round-trip admission ambulatoire**
    - Vérifier que `ref_reservation == None`, `ambulatoire == True`, et que les champs correspondent aux données soumises. Vérifier qu'aucun appel HTTP n'est émis.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 1.1, 1.2, 1.3**

  - [x] 2.3 Écrire le test property-based pour l'admission non ambulatoire (round-trip)
    - **Propriété 2 : Round-trip admission non ambulatoire avec réservation**
    - Vérifier que `ref_reservation == reservation_id` et que les champs correspondent aux données soumises.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 2.1, 2.2, 2.3**

  - [x] 2.4 Écrire le test property-based pour l'échec de réservation
    - **Propriété 3 : Échec de réservation empêche la création en base**
    - Pour tout code HTTP != 201, vérifier qu'une HTTPException est levée et qu'aucune admission n'est persistée.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 3.1, 3.2, 3.3**

- [x] 3. Implémenter les tests de compensation
  - [x] 3.1 Implémenter les tests unitaires de compensation
    - `test_compensation_on_http_exception_reraises_same` : vérifier que la même HTTPException est re-levée après compensation quand la création en base échoue avec HTTPException
    - `test_compensation_failure_logs_print` : vérifier que l'échec de compensation est journalisé via print et que l'erreur originale est propagée
    - _Exigences : 4.3, 5.3_

  - [x] 3.2 Écrire le test property-based pour la compensation après échec BDD
    - **Propriété 4 : Compensation après échec de création en base**
    - Vérifier qu'un appel DELETE est émis avec `reservation_id` et `chambre_id`, et que l'erreur originale est propagée. Utiliser `pytest-mock` pour mocker le repository.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 4.1, 4.2, 4.3**

  - [x] 3.3 Écrire le test property-based pour la résilience de la compensation
    - **Propriété 5 : Résilience de la compensation**
    - Vérifier que l'erreur de compensation ne se propage pas et que l'erreur originale est celle propagée au code appelant.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 5.1, 5.2**

- [x] 4. Checkpoint — Vérifier les tests de création et compensation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implémenter les tests de suppression d'admission
  - [x] 5.1 Implémenter les tests unitaires de suppression
    - `test_delete_returns_admission_deleted_message` : vérifier le retour `{"message": "admission_deleted"}` pour une suppression non ambulatoire avec annulation réussie
    - `test_delete_ambulatoire_returns_admission_deleted` : vérifier le retour `{"message": "admission_deleted"}` pour une suppression ambulatoire sans appel HTTP
    - `test_delete_nonexistent_admission_raises_404` : vérifier HTTPException 404 avec détail `admission_not_found` pour un ID inexistant
    - _Exigences : 6.3, 7.2, 9.1_

  - [x] 5.2 Écrire le test property-based pour la suppression avec annulation
    - **Propriété 6 : Suppression avec annulation de réservation**
    - Vérifier qu'un appel DELETE est émis, que l'admission est supprimée de la base, et que le résultat est `{"message": "admission_deleted"}`.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 6.1, 6.2, 6.3**

  - [x] 5.3 Écrire le test property-based pour la suppression ambulatoire
    - **Propriété 7 : Suppression ambulatoire sans appel HTTP**
    - Vérifier que l'admission est supprimée sans appel HTTP et que le résultat est `{"message": "admission_deleted"}`.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 7.1, 7.2**

  - [x] 5.4 Écrire le test property-based pour l'échec d'annulation
    - **Propriété 8 : Échec d'annulation préserve l'admission**
    - Pour tout code HTTP != 200 et != 404, vérifier qu'une HTTPException 400 est levée avec détail `failed_to_cancel_reservation` et que l'admission reste en base.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 8.1, 8.2, 8.3**

- [x] 6. Checkpoint final — Vérifier l'ensemble des tests
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées avec `*` sont optionnelles (tests property-based) et peuvent être ignorées pour un MVP rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les tests property-based utilisent Hypothesis avec `@settings(max_examples=100)` minimum
- Les tests de compensation utilisent `pytest-mock` pour mocker le repository et simuler les échecs de création en base
- Les tests HTTP utilisent `pytest-httpx` pour mocker les appels vers le Service_Chambres
- Tous les tests sont async (`@pytest.mark.asyncio`)
