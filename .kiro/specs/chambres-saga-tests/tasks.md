# Plan d'implémentation : Tests Saga côté Chambres (participant)

## Vue d'ensemble

Implémentation des tests unitaires et property-based pour le côté participant de la Saga dans le microservice chambres (`cmv_chambres`). Tous les tests sont regroupés dans un fichier unique `cmv_chambres/app/tests/test_chambres_saga.py`, utilisant pytest-asyncio, Hypothesis et les fixtures existantes du `conftest.py` (SQLite en mémoire, tokens JWT, AsyncClient).

## Tâches

- [x] 1. Créer le fichier de test avec les imports, fixtures et générateurs Hypothesis
  - Créer `cmv_chambres/app/tests/test_chambres_saga.py`
  - Ajouter les imports : `pytest`, `pytest-asyncio`, `hypothesis`, `ChambresService`, `PgChambresRepository`, `CreateReservation`, `ReservationResponse`, `Chambre`, `Reservation`, `Service`, `Status`
  - Implémenter les fixtures spécifiques : `chambres_service`, `service_with_free_room`, `service_all_occupied`, `reservation_in_db`
  - Définir les stratégies Hypothesis : `valid_datetimes`, `valid_reservation_data`, `nonexistent_service_ids`, `nonexistent_chambre_ids`, `nonexistent_reservation_ids`, `non_libre_statuses`
  - _Exigences : toutes (1–10)_

- [x] 2. Implémenter les tests de réservation (chemin nominal et erreurs)
  - [x] 2.1 Implémenter les tests unitaires de réservation
    - `test_reservation_success_returns_201` : vérifier le code HTTP 201 et la ReservationResponse avec `reservation_id`, `chambre_id` et `sortie_prevue_le` corrects
    - `test_reservation_no_room_returns_404` : vérifier HTTPException 404 avec détail `no_room_available` quand toutes les chambres sont occupées
    - `test_reservation_nonexistent_service_returns_404` : vérifier HTTPException 404 avec détail `no_room_available` pour un service_id inexistant
    - _Exigences : 1.3, 2.1, 3.1_

  - [x] 2.2 Écrire le test property-based pour le round-trip réservation
    - **Propriété 1 : Round-trip réservation (champs, statut, réponse)**
    - Vérifier que la Reservation créée en base a `ref == patient_id`, `entree_prevue` et `sortie_prevue` correspondant aux données soumises, que la Chambre passe à OCCUPEE, et que la ReservationResponse contient les bons champs.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 1.1, 1.2, 1.3**

  - [x] 2.3 Écrire le test property-based pour aucune chambre disponible
    - **Propriété 2 : Aucune chambre disponible empêche la réservation**
    - Pour tout Service_Hospitalier sans chambre LIBRE, vérifier HTTPException 404, aucune Reservation créée, aucun statut modifié.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 2.1, 2.2, 2.3**

  - [x] 2.4 Écrire le test property-based pour service inexistant
    - **Propriété 3 : Service inexistant empêche la réservation**
    - Pour tout `service_id` inexistant, vérifier HTTPException 404 et aucune Reservation créée.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 3.1, 3.2**

- [x] 3. Implémenter les tests d'annulation (chemin nominal et erreurs)
  - [x] 3.1 Implémenter les tests unitaires d'annulation
    - `test_cancel_success_returns_200` : vérifier le code HTTP 200, la suppression de la Reservation et le statut de la Chambre remis à LIBRE
    - `test_cancel_chambre_not_found_returns_404` : vérifier HTTPException 404 avec détail `chambre_not_found` pour un chambre_id inexistant
    - `test_cancel_reservation_not_found_returns_404` : vérifier HTTPException 404 avec détail `reservation_not_found` pour un reservation_id inexistant, et que la Chambre est tout de même libérée
    - _Exigences : 4.3, 5.1, 6.1, 6.2_

  - [x] 3.2 Écrire le test property-based pour l'annulation nominale
    - **Propriété 4 : Annulation supprime la réservation et libère la chambre**
    - Pour toute Reservation existante avec Chambre OCCUPEE, vérifier la suppression et le passage à LIBRE.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 4.1, 4.2**

  - [x] 3.3 Écrire le test property-based pour chambre introuvable
    - **Propriété 5 : Chambre introuvable empêche l'annulation**
    - Pour tout `chambre_id` inexistant, vérifier HTTPException 404 `chambre_not_found` et aucune Reservation supprimée.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 5.1, 5.2**

  - [x] 3.4 Écrire le test property-based pour réservation introuvable
    - **Propriété 6 : Réservation introuvable libère la chambre puis lève une erreur**
    - Pour tout `reservation_id` inexistant avec `chambre_id` valide, vérifier que la Chambre passe à LIBRE puis HTTPException 404 `reservation_not_found`.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 6.1, 6.2**

- [x] 4. Checkpoint — Vérifier les tests de réservation et d'annulation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implémenter les tests round-trip et sélection de chambre
  - [x] 5.1 Écrire le test property-based pour le round-trip réservation → annulation
    - **Propriété 7 : Round-trip réservation → annulation**
    - Vérifier que le cycle complet remet la Chambre à LIBRE, supprime la Reservation, et laisse le nombre total de Reservations identique au nombre initial.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 7.1, 7.2, 7.3**

  - [-] 5.2 Écrire le test property-based pour la sélection de chambre disponible
    - **Propriété 8 : Sélection de chambre disponible**
    - Vérifier que `get_available_room` retourne une Chambre LIBRE du bon service, ou lève HTTPException 404 si aucune n'est LIBRE.
    - `@settings(max_examples=100)`
    - **Valide : Exigences 8.1, 8.2, 8.3**

- [ ] 6. Implémenter les tests de validation et d'authentification
  - [~] 6.1 Implémenter les tests de validation Pydantic
    - `test_reservation_missing_fields_returns_422` : vérifier HTTP 422 quand les champs requis sont absents
    - `test_reservation_invalid_datetime_returns_422` : vérifier HTTP 422 quand les types datetime sont invalides
    - _Exigences : 9.1, 9.2_

  - [~] 6.2 Implémenter les tests d'authentification JWT
    - `test_reservation_no_token_returns_401` : vérifier HTTP 401 avec détail `Not authenticated` sans token
    - `test_reservation_invalid_token_returns_403` : vérifier HTTP 403 avec détail `not_authorized` avec token invalide
    - `test_reservation_valid_sources_accepted` : vérifier que les sources `api_patients` et `api_gateway` sont acceptées
    - _Exigences : 10.1, 10.2, 10.3_

- [~] 7. Checkpoint final — Vérifier l'ensemble des tests
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées avec `*` sont optionnelles (tests property-based) et peuvent être ignorées pour un MVP rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les tests property-based utilisent Hypothesis avec `@settings(max_examples=100)` minimum
- Les tests unitaires passent par le routeur via `AsyncClient` pour valider l'intégration complète (auth, validation Pydantic, codes HTTP)
- Les tests property-based ciblent `ChambresService` directement pour isoler la logique métier
- Tous les tests sont async (`@pytest.mark.asyncio`)
