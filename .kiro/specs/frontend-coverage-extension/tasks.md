# Plan d'Implémentation — Extension de la Couverture de Tests Frontend

## Vue d'ensemble

Implémentation incrémentale des tests unitaires et property-based complémentaires pour le frontend Vue.js du projet CMV Healthcare. Les tâches ciblent les composants de dialogue, les interactions avancées des composants de liste, le composable useLogin (sans mock), les fonctions manquantes du store utilisateur, et les interactions avancées des vues AdmissionView et PatientView.

## Tâches

- [x] 1. Implémenter les tests du composant DeletePatientDialog
  - [x] 1.1 Créer `src/tests/DeletePatientDialog.spec.ts`
    - Monter le composant avec un patient mock et visible=true via des stubs PrimeVue (Dialog, Button)
    - Vérifier que le nom, le prénom et la date de naissance du patient sont affichés dans le dialogue
    - Vérifier que le clic sur "Confirmer" émet l'événement "confirm"
    - Vérifier que le clic sur "Annuler" émet l'événement "cancel"
    - Vérifier que la fermeture du Dialog (update:visible) émet "cancel"
    - _Exigences : 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implémenter les tests du composant DeleteConfirmationDialog
  - [x] 2.1 Créer `src/tests/DeleteConfirmationDialog.spec.ts`
    - Monter le composant avec un document mock et visible=true via des stubs PrimeVue
    - Vérifier que le type de document est affiché dans le dialogue
    - Vérifier que le clic sur le bouton de confirmation émet "confirm"
    - Vérifier que le clic sur le bouton d'annulation émet "cancel"
    - Vérifier que le bouton de confirmation affiche un état de chargement quand loading=true
    - Vérifier que le bloc type de document est masqué quand document est null
    - _Exigences : 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Implémenter les tests du composant DocumentPatient
  - [x] 3.1 Créer `src/tests/DocumentPatient.spec.ts` avec les tests unitaires
    - Monter le composant avec un document mock et un index via des stubs PrimeVue (Card, Button)
    - Vérifier que le numéro du document (index + 1), la date de création et le type de document sont affichés
    - Mocker window.open et vérifier l'appel avec l'URL correcte lors du clic sur téléchargement
    - Vérifier que le clic sur suppression émet "delete-document" avec l'identifiant du document
    - _Exigences : 3.1, 3.2, 3.3_

  - [x] 3.2 Écrire le test property-based pour l'URL de téléchargement
    - **Propriété 1 : URL de téléchargement contient l'identifiant du document**
    - Utiliser `fc.integer({ min: 1, max: 100000 })` pour générer des IDs
    - Monter DocumentPatient avec chaque ID, cliquer sur téléchargement, vérifier que window.open contient l'ID
    - **Valide : Exigences 3.2**

  - [x] 3.3 Écrire le test property-based pour l'émission de suppression
    - **Propriété 2 : Émission de suppression contient l'identifiant du document**
    - Utiliser `fc.integer({ min: 1, max: 100000 })` pour générer des IDs
    - Monter DocumentPatient avec chaque ID, cliquer sur suppression, vérifier l'événement émis
    - **Valide : Exigences 3.3**

- [x] 4. Étendre les tests du composant ListPatients
  - [x] 4.1 Ajouter les tests d'interactions avancées dans `src/tests/ListPatients.spec.ts`
    - Tester le rendu du message "aucun patient" quand la liste est vide (result = [])
    - Tester la mise à jour de search lors de la saisie dans le champ de recherche
    - Tester l'appel de onResetFilter lors du clic sur l'icône de réinitialisation
    - Tester l'appel de showDeleteDialog avec les données du patient lors du clic sur le bouton de suppression
    - Tester le rendu de DeletePatientDialog quand selectedPatient est défini et dialogVisible est true
    - _Exigences : 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Étendre les tests du composant DocumentsList
  - [x] 5.1 Ajouter les tests du cycle de suppression dans `src/tests/DocumentsList.spec.ts`
    - Tester que le clic sur suppression d'un DocumentPatient met à jour documentToDelete et rend visible le DeleteConfirmationDialog
    - Tester que la confirmation de suppression appelle deleteDocument avec l'identifiant du document
    - Tester que l'annulation réinitialise documentToDelete à null et visible à false
    - _Exigences : 5.1, 5.2, 5.3_

- [x] 6. Étendre les tests du composant DocumentUploadDialog
  - [x] 6.1 Ajouter les tests de cas limites dans `src/tests/DocumentUploadDialog.spec.ts`
    - Vérifier que le bouton de soumission est désactivé quand aucun fichier et aucun type ne sont sélectionnés
    - Vérifier que selectedFile est réinitialisé à null après suppression du fichier via le bouton de suppression
    - Vérifier que onSubmit est appelé lors de la soumission avec un fichier et un type valides
    - _Exigences : 6.1, 6.2, 6.3_

- [x] 7. Checkpoint — Vérifier les tests des composants
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

- [x] 8. Réécrire les tests du composable useLogin (sans mock du composable)
  - [x] 8.1 Réécrire `src/tests/UseLogin.spec.ts` avec la logique réelle
    - Mocker useHttp (sendRequest, isLoading, error) au niveau module, mais NE PAS mocker useLogin
    - Mocker useToast, vue-i18n, useUserStore
    - Vérifier l'état initial : error null, isLoading false, initialValues avec username et password vides
    - Vérifier que onSubmit appelle sendRequest avec path "/auth/login", method "post" et body contenant les identifiants
    - Vérifier que getUserInfos est appelé quand la requête réussit avec success=true
    - Vérifier qu'un toast d'erreur est affiché quand error devient non null
    - Vérifier que loginFormSchema rejette un email invalide et un mot de passe non conforme
    - _Exigences : 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Étendre les tests du Store Utilisateur
  - [x] 9.1 Ajouter les tests de toggleColorScheme, updateColorScheme et handshake dans `src/tests/UserStore.spec.ts`
    - Tester toggleColorScheme depuis mode "light" : classe "dark" ajoutée à html, mode passe à "dark", localStorage mis à jour
    - Tester toggleColorScheme depuis mode "dark" : classe "dark" retirée de html, mode repasse à "light", localStorage nettoyé
    - Tester updateColorScheme avec localStorage contenant "dark" : mode mis à "dark", classe "dark" ajoutée
    - Tester updateColorScheme sans localStorage "color-scheme" : mode reste "light"
    - Tester handshake : vérifier que updateColorScheme et getUserInfos sont exécutés
    - _Exigences : 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 10. Checkpoint — Vérifier les tests du composable et du store
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

- [x] 11. Étendre les tests de AdmissionView (interactions avancées)
  - [x] 11.1 Ajouter les tests d'interactions dans `src/tests/BusinessViews.spec.ts` (section AdmissionView)
    - Mocker sendRequest pour capturer les appels POST
    - Tester la soumission du formulaire : sendRequest appelé avec path "/patients/admissions", method "POST", body contenant patient_id, ambulatoire, entree_le, sortie_prevue_le, service_id
    - Tester le toast de succès et la navigation vers /patient/{patientId} après création réussie
    - Tester le clic sur "Estimer la durée du séjour" : sendRequest appelé avec path "/ml/predictions/predict", method "POST"
    - Tester le toast d'erreur en cas d'échec de soumission
    - Tester le clic sur "Annuler" : router.back() appelé
    - _Exigences : 9.1, 9.2, 9.3, 9.5, 9.6_

  - [x] 11.2 Écrire le test property-based pour l'arithmétique de date de prédiction
    - **Propriété 3 : Arithmétique de date pour l'application de la prédiction**
    - Utiliser `fc.integer({ min: 1, max: 365 })` pour générer des nombres de jours
    - Vérifier que la date de sortie = date d'entrée + nombre de jours prédit
    - Vérifier que ambulatoire passe à "Non ambulatoire"
    - **Valide : Exigences 9.4**

- [x] 12. Étendre les tests de PatientView (interactions avancées)
  - [x] 12.1 Ajouter les tests d'interactions dans `src/tests/BusinessViews.spec.ts` (section PatientView)
    - Vérifier que fetchPatientData est appelé avec l'ID numérique de la route au montage
    - Tester le basculement en mode édition : émettre toggle-editing depuis PatientActions, vérifier que PatientForm est affiché et PatientDetail masqué
    - Tester le retour en mode lecture : cliquer sur "Retour aux informations du patient", vérifier que PatientDetail est affiché
    - Tester que toggleVisible met à jour la prop visible de DocumentUpload
    - Tester que quand detailPatient est null, PatientDetail, DocumentsList et DocumentUpload ne sont pas rendus
    - _Exigences : 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 13. Checkpoint final — Vérifier l'ensemble de la suite de tests
  - Exécuter `cd cmv_gateway/cmv_front && npx vitest --run` et s'assurer que tous les tests passent
  - Demander à l'utilisateur s'il y a des questions ou ajustements nécessaires

## Notes

- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les fichiers existants (ListPatients.spec.ts, DocumentsList.spec.ts, etc.) sont étendus, pas remplacés
- UseLogin.spec.ts est réécrit pour tester la logique réelle au lieu de mocker le composable
- Les tests property-based utilisent fast-check (déjà installé) avec minimum 100 itérations
- Les checkpoints assurent une validation incrémentale
