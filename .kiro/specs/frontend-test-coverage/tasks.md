# Plan d'Implémentation : Couverture de Tests Frontend

## Vue d'ensemble

Implémentation incrémentale des tests unitaires et property-based pour le frontend Vue.js du projet CMV Healthcare. Les tâches sont organisées par priorité : composables (logique métier critique), puis vues, puis store/routeur/utilitaires. Chaque tâche construit sur les précédentes, en commençant par l'installation des dépendances et les composables fondamentaux.

## Tâches

- [x] 1. Installer fast-check et préparer l'environnement de test
  - Exécuter `npm install -D fast-check` dans `cmv_gateway/cmv_front/`
  - Vérifier que l'import `import fc from 'fast-check'` fonctionne dans un fichier de test
  - _Exigences : toutes (prérequis pour les tests property-based)_

- [x] 2. Implémenter les tests du composable useHttp
  - [x] 2.1 Créer `src/tests/UseHttp.spec.ts` avec les tests unitaires
    - Mocker axios au niveau module avec `vi.mock('axios')`
    - Tester la requête réussie : `sendRequest` retourne les données, `isLoading` passe de true à false
    - Tester l'erreur serveur (status >= 500) : redirection vers "network-issue"
    - Tester l'erreur 401 : tentative de refresh token via /auth/refresh
    - Tester l'échec du refresh : appel `userStore.logout()`
    - Tester que `error` contient le message `detail` de la réponse API
    - Tester que FormData n'a pas de Content-Type forcé à application/json
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 2.2 Écrire le test property-based pour la transition isLoading
    - **Propriété 1 : Transition isLoading sur requête réussie**
    - **Valide : Exigences 1.1**

  - [x] 2.3 Écrire le test property-based pour la redirection sur erreur serveur
    - **Propriété 2 : Redirection sur erreur serveur (status >= 500)**
    - **Valide : Exigences 1.2**

  - [x] 2.4 Écrire le test property-based pour la capture du message d'erreur
    - **Propriété 3 : Capture du message d'erreur API**
    - **Valide : Exigences 1.5**

- [x] 3. Implémenter les tests du composable useLazyLoad
  - [x] 3.1 Créer `src/tests/UseLazyLoad.spec.ts` avec les tests unitaires
    - Mocker useHttp pour intercepter les appels `sendRequest`
    - Tester les valeurs par défaut de `lazyState` (first: 0, rows: 10, sortField: "nom", sortOrder: 1)
    - Tester la mise à jour de `lazyState` via `onLazyLoad` avec un événement de pagination
    - Tester la réinitialisation de `first` à 0 lors de `onSort`
    - Tester le debounce de 300ms sur la recherche avec `vi.useFakeTimers()`
    - Tester la réinitialisation de `search` via `onResetFilter`
    - Tester la construction correcte des paramètres HTTP dans `getData`
    - _Exigences : 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 3.2 Écrire le test property-based pour la mise à jour de lazyState par pagination
    - **Propriété 4 : Mise à jour de lazyState par pagination**
    - **Valide : Exigences 2.2**

  - [x] 3.3 Écrire le test property-based pour la réinitialisation de first lors du tri
    - **Propriété 5 : Réinitialisation de first lors du tri**
    - **Valide : Exigences 2.3**

  - [x] 3.4 Écrire le test property-based pour la construction des paramètres URL
    - **Propriété 6 : Construction correcte des paramètres URL de getData**
    - **Valide : Exigences 2.6**

- [x] 4. Implémenter les tests du composable useChambresList
  - [x] 4.1 Créer `src/tests/UseChambresList.spec.ts` avec les tests unitaires
    - Mocker useHttp pour simuler les réponses de `/chambres/services`
    - Tester l'appel GET vers /chambres/services via `getChambres`
    - Tester le filtrage par préfixe insensible à la casse via `search`
    - Tester la réinitialisation de la liste quand la recherche ne trouve rien
    - Tester `searchBySelect` avec mise à jour de `searchValue` et filtrage par préfixe exact
    - Tester `resetSearchValue` et la réinitialisation quand `searchValue` est vidé
    - _Exigences : 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 4.2 Écrire le test property-based pour le filtrage par préfixe des services
    - **Propriété 7 : Filtrage par préfixe des services**
    - **Valide : Exigences 3.2, 3.4**

- [x] 5. Implémenter les tests du composable useListPatients
  - [x] 5.1 Créer `src/tests/UseListPatients.spec.ts` avec les tests unitaires
    - Mocker useHttp et useLazyLoad
    - Tester `showDeleteDialog` : mise à jour de `selectedPatient` et `dialogVisible` à true
    - Tester `onCancel` : réinitialisation de `selectedPatient` à null et `dialogVisible` à false
    - Tester `onConfirm` : requête DELETE avec l'ID du patient, fermeture du dialogue
    - Tester le toast de succès et le rappel de `getData` après suppression réussie
    - Tester le toast d'erreur en cas d'échec de suppression
    - _Exigences : 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 5.2 Écrire le test property-based pour showDeleteDialog
    - **Propriété 8 : showDeleteDialog met à jour l'état du dialogue**
    - **Valide : Exigences 4.1**

- [x] 6. Implémenter les tests des composables usePatient et usePatientForm
  - [x] 6.1 Créer `src/tests/UsePatient.spec.ts` avec les tests unitaires
    - Mocker useHttp
    - Tester que `detailPatient` est null à l'initialisation
    - Tester l'appel GET vers `/patients/patients/detail/{id}` via `fetchPatientData`
    - _Exigences : 5.1, 5.2_

  - [x] 6.2 Écrire le test property-based pour la construction de l'URL fetchPatientData
    - **Propriété 9 : Construction de l'URL fetchPatientData**
    - **Valide : Exigences 5.2**

  - [x] 6.3 Créer `src/tests/UsePatientForm.spec.ts` avec les tests unitaires
    - Mocker useHttp, vue-router, useToast
    - Tester l'initialisation : `civilites` contient ["Monsieur", "Madame", "Autre"], `isEditing` est false
    - Tester `onCreatePatient` : requête POST vers /patients/patients avec date formatée (heures à 12h)
    - Tester la navigation vers /patient/{id} après création réussie et toast de succès
    - Tester `onUpdatePatient` : requête PUT vers /patients/patients/{id}, `isEditing` repasse à false
    - Tester le toast d'erreur en cas d'échec de soumission
    - _Exigences : 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.4 Écrire le test property-based pour le formatage de la date à midi
    - **Propriété 10 : Formatage de la date à midi lors de la création patient**
    - **Valide : Exigences 6.2**

- [x] 7. Checkpoint — Vérifier les tests des composables principaux
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

- [x] 8. Implémenter les tests des composables useDocuments, useDocumentManagement et useUploadDocument
  - [x] 8.1 Créer `src/tests/UseDocuments.spec.ts` avec les tests unitaires
    - Mocker useToast et useI18n
    - Tester que `visible` est false à l'initialisation
    - Tester le toggle de `visible` via `toggleVisible`
    - Tester `handleUploadSuccess` : toast de succès et appel de `refreshData` avec le patientId
    - _Exigences : 7.1, 7.2, 7.3_

  - [x] 8.2 Écrire le test property-based pour l'idempotence du double toggle
    - **Propriété 11 : Idempotence du double toggle de visibilité**
    - **Valide : Exigences 7.2**

  - [x] 8.3 Créer `src/tests/UseDocumentManagement.spec.ts` avec les tests unitaires
    - Mocker useHttp et useToast
    - Tester que `visible` est false et `documentToDelete` est null à l'initialisation
    - Tester `deleteDocument` : requête DELETE vers `/patients/delete/documents/delete/{id}`
    - Tester le toast de succès, l'exécution du callback onSuccess, et la réinitialisation de `documentToDelete`
    - _Exigences : 8.1, 8.2, 8.3_

  - [x] 8.4 Écrire le test property-based pour la construction de l'URL de suppression
    - **Propriété 12 : Construction de l'URL de suppression de document**
    - **Valide : Exigences 8.2**

  - [x] 8.5 Créer `src/tests/UseUploadDocument.spec.ts` avec les tests unitaires
    - Mocker useHttp et useToast
    - Tester que `documentTypes` contient 8 types et que `isValid` est false à l'initialisation
    - Tester que `isValid` passe à true quand fichier et type sont sélectionnés
    - Tester `onSubmit` : requête POST multipart/form-data vers `/patients/upload/documents/create/{patientId}`
    - Tester les émissions d'événements "refresh" et "update:visible" après succès, et la réinitialisation
    - Tester le toast d'erreur en cas d'échec de téléversement
    - _Exigences : 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 8.6 Écrire le test property-based pour la validité du formulaire d'upload
    - **Propriété 13 : Validité du formulaire d'upload**
    - **Valide : Exigences 9.2**

- [x] 9. Implémenter les tests des vues simples et layout
  - [x] 9.1 Créer `src/tests/SimpleViews.spec.ts` avec les tests unitaires
    - Mocker les composants enfants (LoginForm) et le routeur
    - Tester le rendu de LoginForm dans LoginView
    - Tester le message 404 et le lien de retour dans NotFound
    - Tester le message de problème serveur dans NetworkIssue
    - _Exigences : 10.1, 10.2, 10.3_

  - [x] 9.2 Créer `src/tests/LayoutViews.spec.ts` avec les tests unitaires
    - Mocker RouterView
    - Tester la présence de RouterView dans AccueilLayout
    - Tester la présence de RouterView dans ChambresLayout
    - _Exigences : 11.1, 11.2_

- [x] 10. Implémenter les tests des vues métier
  - [x] 10.1 Créer `src/tests/BusinessViews.spec.ts` avec les tests unitaires
    - Mocker les composants enfants (PageHeader, ListPatients, PatientDetail, DocumentsList, PatientForm, PatientDataDisclaimer, AutoComplete)
    - Mocker les composables associés (usePatient, useChambresList, useListPatients)
    - Tester AccueilView : rendu de PageHeader et ListPatients
    - Tester PatientView : appel de `fetchPatientData` avec l'ID de la route, rendu de PatientDetail et DocumentsList
    - Tester AddPatientView : rendu de PatientForm et PatientDataDisclaimer
    - Tester ChambresView : rendu de PageHeader et barre de recherche AutoComplete
    - Tester AdmissionView : rendu du formulaire avec champs date d'entrée, date de sortie, ambulatoire et services
    - _Exigences : 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 11. Checkpoint — Vérifier les tests des vues
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

- [x] 12. Implémenter les tests du store utilisateur
  - [x] 12.1 Créer `src/tests/UserStore.spec.ts` avec les tests unitaires
    - Utiliser `createTestingPinia` de @pinia/testing
    - Tester l'état initial : `role` chaîne vide, `mode` "light", `authChecked` false
    - Tester `getUserInfos` succès : `role` mis à jour, `authChecked` passe à true
    - Tester `getUserInfos` échec : `authChecked` passe à true malgré l'erreur
    - Tester `signout` : `role` réinitialisé, requête POST vers /auth/logout
    - Tester `logout` : `role` réinitialisé, redirection vers la route racine
    - _Exigences : 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 13. Implémenter les tests du routeur
  - [x] 13.1 Créer `src/tests/Router.spec.ts` avec les tests unitaires
    - Mocker le store utilisateur pour simuler différents rôles
    - Tester l'affichage de LoginView pour un utilisateur non authentifié sur "/"
    - Tester la redirection vers /accueil pour un utilisateur avec rôle "home" sur "/"
    - Tester la redirection vers "/" pour un utilisateur sans rôle "home" accédant à /accueil
    - Tester l'affichage de NotFound pour une route inexistante
    - Tester l'accès autorisé à /chambres pour les rôles "home", "nurses", "cleaning"
    - _Exigences : 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 13.2 Écrire le test property-based pour les routes inexistantes
    - **Propriété 14 : Routes inexistantes affichent NotFound**
    - **Valide : Exigences 14.4**

  - [x] 13.3 Écrire le test property-based pour l'accès aux chambres par rôle
    - **Propriété 15 : Accès aux chambres par rôles autorisés**
    - **Valide : Exigences 14.5**

- [x] 14. Implémenter les tests des utilitaires regex
  - [x] 14.1 Créer `src/tests/Regex.spec.ts` avec les tests unitaires
    - Tester `regexMail` avec des exemples concrets d'emails valides et invalides
    - Tester `regexPassword` avec des mots de passe conformes et non conformes (12+ chars, majuscule, minuscule, chiffre, caractère spécial)
    - Tester `regexGeneric` avec des chaînes alphanumériques valides (accents français inclus) et des chaînes contenant des caractères interdits
    - _Exigences : 15.1, 15.2, 15.3_

  - [x] 14.2 Écrire le test property-based pour la validation regex email
    - **Propriété 16 : Validation regex email**
    - **Valide : Exigences 15.1**

  - [x] 14.3 Écrire le test property-based pour la validation regex mot de passe
    - **Propriété 17 : Validation regex mot de passe**
    - **Valide : Exigences 15.2**

  - [x] 14.4 Écrire le test property-based pour la validation regex générique
    - **Propriété 18 : Validation regex générique**
    - **Valide : Exigences 15.3**

- [x] 15. Checkpoint final — Vérifier l'ensemble de la suite de tests
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être ignorées pour un MVP plus rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints assurent une validation incrémentale
- Les tests property-based valident les propriétés universelles de correction
- Les tests unitaires valident des exemples concrets et des cas limites
- fast-check doit être installé avant toute tâche property-based
