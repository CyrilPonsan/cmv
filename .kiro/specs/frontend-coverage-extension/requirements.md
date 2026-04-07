# Document d'Exigences — Extension de la Couverture de Tests Frontend

## Introduction

Ce document définit les exigences pour étendre la couverture de tests unitaires des composants Vue.js, composables et stores du frontend CMV Healthcare (`cmv_gateway/cmv_front/src/`). Le projet dispose déjà d'une première vague de tests (spec `frontend-test-coverage`) couvrant les composables, les vues en shallow mount, le routeur et les utilitaires regex. Cette nouvelle spec cible les fichiers dont la couverture reste insuffisante : les composants de dialogue (DeletePatientDialog, DeleteConfirmationDialog, DocumentPatient), les composants de liste (ListPatients, DocumentsList, DocumentUploadDialog), le composable useLogin (testé à 5%), les fonctions manquantes du store utilisateur (toggleColorScheme, handshake), et les interactions avancées des vues AdmissionView et PatientView.

## Glossaire

- **Suite_de_Tests** : Ensemble de tests Vitest couvrant un fichier source donné
- **Composant** : Composant Vue 3 avec `<script setup>` utilisant la Composition API
- **Composable** : Fonction réutilisable Vue 3 encapsulant de la logique métier avec état réactif
- **Mock** : Substitut de dépendance (API HTTP, store, router, i18n) utilisé pour isoler le code testé
- **Store_Utilisateur** : Store Pinia gérant l'authentification, le rôle et les préférences utilisateur
- **Dialogue** : Composant modal PrimeVue (Dialog) utilisé pour les confirmations et formulaires
- **Émission** : Événement Vue émis par un composant enfant vers son parent via `emit`
- **Toast** : Notification PrimeVue affichée temporairement pour informer l'utilisateur d'un résultat

## Exigences

### Exigence 1 : Tests du composant DeletePatientDialog

**User Story :** En tant que développeur, je veux tester le composant DeletePatientDialog, afin de garantir l'affichage correct des informations du patient et le bon fonctionnement des boutons de confirmation et d'annulation.

#### Critères d'acceptation

1. WHEN DeletePatientDialog est monté avec un patient et visible à true, THE Suite_de_Tests SHALL vérifier que le nom, le prénom et la date de naissance du patient sont affichés dans le Dialogue
2. WHEN l'utilisateur clique sur le bouton "Confirmer", THE Suite_de_Tests SHALL vérifier que l'Émission "confirm" est déclenchée
3. WHEN l'utilisateur clique sur le bouton "Annuler", THE Suite_de_Tests SHALL vérifier que l'Émission "cancel" est déclenchée
4. WHEN le Dialogue est fermé via le bouton de fermeture (update:visible), THE Suite_de_Tests SHALL vérifier que l'Émission "cancel" est déclenchée

### Exigence 2 : Tests du composant DeleteConfirmationDialog (documents)

**User Story :** En tant que développeur, je veux tester le composant DeleteConfirmationDialog, afin de garantir l'affichage correct du type de document et le bon fonctionnement des actions de confirmation et d'annulation.

#### Critères d'acceptation

1. WHEN DeleteConfirmationDialog est monté avec un document et visible à true, THE Suite_de_Tests SHALL vérifier que le type de document est affiché dans le Dialogue
2. WHEN l'utilisateur clique sur le bouton de confirmation, THE Suite_de_Tests SHALL vérifier que l'Émission "confirm" est déclenchée
3. WHEN l'utilisateur clique sur le bouton d'annulation, THE Suite_de_Tests SHALL vérifier que l'Émission "cancel" est déclenchée
4. WHILE loading est true, THE Suite_de_Tests SHALL vérifier que le bouton de confirmation affiche un état de chargement
5. WHEN le document est null, THE Suite_de_Tests SHALL vérifier que le bloc d'affichage du type de document est masqué

### Exigence 3 : Tests du composant DocumentPatient

**User Story :** En tant que développeur, je veux tester le composant DocumentPatient, afin de garantir l'affichage correct des informations du document et le bon fonctionnement des boutons de téléchargement et de suppression.

#### Critères d'acceptation

1. WHEN DocumentPatient est monté avec un document et un index, THE Suite_de_Tests SHALL vérifier que le numéro du document (index + 1), la date de création et le type de document sont affichés
2. WHEN l'utilisateur clique sur le bouton de téléchargement, THE Suite_de_Tests SHALL vérifier que window.open est appelé avec l'URL correcte contenant l'identifiant du document
3. WHEN l'utilisateur clique sur le bouton de suppression, THE Suite_de_Tests SHALL vérifier que l'Émission "delete-document" est déclenchée avec l'identifiant du document

### Exigence 4 : Tests approfondis du composant ListPatients

**User Story :** En tant que développeur, je veux approfondir les tests du composant ListPatients, afin de couvrir les interactions utilisateur (recherche, suppression, navigation) au-delà du rendu de base.

#### Critères d'acceptation

1. WHEN la liste des patients est vide, THE Suite_de_Tests SHALL vérifier que le DataTable affiche le message "aucun patient" au lieu du tableau
2. WHEN l'utilisateur saisit un terme dans le champ de recherche, THE Suite_de_Tests SHALL vérifier que la valeur de search est mise à jour
3. WHEN l'utilisateur clique sur l'icône de réinitialisation de la recherche, THE Suite_de_Tests SHALL vérifier que onResetFilter est appelé
4. WHEN l'utilisateur clique sur le bouton de suppression d'un patient, THE Suite_de_Tests SHALL vérifier que showDeleteDialog est appelé avec les données du patient
5. WHEN selectedPatient est défini et dialogVisible est true, THE Suite_de_Tests SHALL vérifier que le composant DeletePatientDialog est rendu

### Exigence 5 : Tests approfondis du composant DocumentsList

**User Story :** En tant que développeur, je veux approfondir les tests du composant DocumentsList, afin de couvrir le cycle complet de suppression de document avec le dialogue de confirmation.

#### Critères d'acceptation

1. WHEN l'utilisateur clique sur le bouton de suppression d'un DocumentPatient, THE Suite_de_Tests SHALL vérifier que documentToDelete est mis à jour et que le DeleteConfirmationDialog devient visible
2. WHEN l'utilisateur confirme la suppression dans le DeleteConfirmationDialog, THE Suite_de_Tests SHALL vérifier que deleteDocument est appelé avec l'identifiant du document
3. WHEN l'utilisateur annule la suppression dans le DeleteConfirmationDialog, THE Suite_de_Tests SHALL vérifier que documentToDelete est réinitialisé à null et que visible repasse à false

### Exigence 6 : Tests approfondis du composant DocumentUploadDialog

**User Story :** En tant que développeur, je veux approfondir les tests du composant DocumentUploadDialog, afin de couvrir les cas limites de validation et d'interaction avec le formulaire de téléversement.

#### Critères d'acceptation

1. WHEN aucun fichier et aucun type de document ne sont sélectionnés, THE Suite_de_Tests SHALL vérifier que le bouton de soumission est désactivé
2. WHEN un fichier est sélectionné puis supprimé via le bouton de suppression, THE Suite_de_Tests SHALL vérifier que selectedFile est réinitialisé à null
3. WHEN le formulaire est soumis avec un fichier et un type valides, THE Suite_de_Tests SHALL vérifier que onSubmit est appelé

### Exigence 7 : Tests du composable useLogin (couverture réelle)

**User Story :** En tant que développeur, je veux tester le composable useLogin sans le mocker, afin de garantir la logique réelle de connexion, de validation et de gestion d'erreurs.

#### Critères d'acceptation

1. WHEN useLogin est initialisé, THE Suite_de_Tests SHALL vérifier que error est null, isLoading est false et initialValues contient username et password vides
2. WHEN onSubmit est appelé avec des identifiants valides et que la requête réussit, THE Suite_de_Tests SHALL vérifier que sendRequest est appelé avec le chemin "/auth/login", la méthode "post" et le corps contenant les identifiants
3. WHEN la requête de connexion réussit avec success à true, THE Suite_de_Tests SHALL vérifier que getUserInfos du Store_Utilisateur est appelé
4. WHEN une erreur de connexion survient (error non null), THE Suite_de_Tests SHALL vérifier qu'un Toast d'erreur est affiché avec le message de connexion échouée
5. THE Suite_de_Tests SHALL vérifier que loginFormSchema rejette un email invalide et un mot de passe non conforme à regexPassword

### Exigence 8 : Tests des fonctions manquantes du Store_Utilisateur

**User Story :** En tant que développeur, je veux tester les fonctions toggleColorScheme, updateColorScheme et handshake du Store_Utilisateur, afin de couvrir la gestion du thème clair/sombre et l'initialisation de l'application.

#### Critères d'acceptation

1. WHEN toggleColorScheme est appelé et que le mode est "light", THE Suite_de_Tests SHALL vérifier que la classe "dark" est ajoutée à l'élément HTML et que mode passe à "dark"
2. WHEN toggleColorScheme est appelé et que le mode est "dark", THE Suite_de_Tests SHALL vérifier que la classe "dark" est retirée de l'élément HTML et que mode repasse à "light"
3. WHEN updateColorScheme est appelé et que localStorage contient "dark" pour "color-scheme", THE Suite_de_Tests SHALL vérifier que mode est mis à "dark" et que la classe "dark" est ajoutée à l'élément HTML
4. WHEN updateColorScheme est appelé et que localStorage ne contient pas "color-scheme", THE Suite_de_Tests SHALL vérifier que mode reste "light"
5. WHEN handshake est appelé, THE Suite_de_Tests SHALL vérifier que updateColorScheme et getUserInfos sont exécutés


### Exigence 9 : Tests des interactions avancées de AdmissionView

**User Story :** En tant que développeur, je veux tester les interactions avancées de AdmissionView, afin de couvrir la soumission du formulaire d'admission, la prédiction IA et la gestion d'erreurs.

#### Critères d'acceptation

1. WHEN le formulaire d'admission est soumis avec des données valides, THE Suite_de_Tests SHALL vérifier que sendRequest est appelé avec le chemin "/patients/admissions", la méthode "POST" et un corps contenant patient_id, ambulatoire, entree_le, sortie_prevue_le et service_id
2. WHEN la création d'admission réussit, THE Suite_de_Tests SHALL vérifier qu'un Toast de succès est affiché et que le routeur navigue vers /patient/{patientId}
3. WHEN le bouton "Estimer la durée du séjour" est cliqué, THE Suite_de_Tests SHALL vérifier que sendRequest est appelé avec le chemin "/ml/predictions/predict" et la méthode "POST"
4. WHEN la prédiction réussit et que l'utilisateur clique sur "Appliquer l'estimation", THE Suite_de_Tests SHALL vérifier que la date de sortie est mise à jour en ajoutant le nombre de jours prédit à la date d'entrée et que ambulatoire passe à "Non ambulatoire"
5. IF une erreur survient lors de la soumission de l'admission, THEN THE Suite_de_Tests SHALL vérifier qu'un Toast d'erreur est affiché avec le message d'erreur
6. WHEN le bouton "Annuler" est cliqué, THE Suite_de_Tests SHALL vérifier que router.back() est appelé

### Exigence 10 : Tests des interactions avancées de PatientView

**User Story :** En tant que développeur, je veux tester les interactions avancées de PatientView, afin de couvrir le basculement entre mode lecture et mode édition, et la gestion des documents.

#### Critères d'acceptation

1. WHEN PatientView est montée avec un ID de patient valide, THE Suite_de_Tests SHALL vérifier que fetchPatientData est appelé avec l'ID numérique de la route
2. WHEN l'utilisateur bascule en mode édition via PatientActions, THE Suite_de_Tests SHALL vérifier que le composant PatientForm est affiché à la place de PatientDetail
3. WHEN l'utilisateur clique sur "Retour aux informations du patient" en mode édition, THE Suite_de_Tests SHALL vérifier que isEditing repasse à false et que PatientDetail est de nouveau affiché
4. WHEN toggleVisible est appelé, THE Suite_de_Tests SHALL vérifier que le composant DocumentUpload reçoit la prop visible mise à jour
5. WHEN detailPatient est null (chargement en cours), THE Suite_de_Tests SHALL vérifier que les sections PatientDetail, DocumentsList et DocumentUpload ne sont pas rendues
