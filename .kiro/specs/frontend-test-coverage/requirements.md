# Document d'Exigences — Couverture de Tests Frontend

## Introduction

Ce document définit les exigences pour améliorer la couverture de tests unitaires du frontend Vue.js du projet CMV Healthcare (`cmv_gateway/cmv_front/src/`). Le projet utilise Vitest, @vue/test-utils et happy-dom. Actuellement, 10 fichiers sont testés. L'objectif est de couvrir les composables (logique métier, priorité haute) et les vues non testées, en suivant les conventions établies par les tests existants.

## Glossaire

- **Suite_de_Tests** : Ensemble de tests Vitest couvrant un fichier source donné
- **Composable** : Fonction réutilisable Vue 3 (Composition API) encapsulant de la logique métier avec état réactif
- **Vue** : Composant Vue représentant une page complète, associé à une route du routeur
- **Mock** : Substitut de dépendance (API HTTP, store, router) utilisé pour isoler le code testé
- **Couverture** : Pourcentage de lignes/branches de code source exécutées par les tests
- **Store_Utilisateur** : Store Pinia gérant l'authentification, le rôle et les préférences utilisateur
- **Routeur** : Instance vue-router gérant la navigation et la protection des routes par rôle

## Exigences

### Exigence 1 : Tests du composable useHttp

**User Story :** En tant que développeur, je veux tester le composable useHttp, afin de garantir la fiabilité des requêtes HTTP, du rafraîchissement de tokens et de la gestion d'erreurs.

#### Critères d'acceptation

1. WHEN une requête HTTP est envoyée avec succès, THE Suite_de_Tests SHALL vérifier que sendRequest retourne les données et que isLoading passe de true à false
2. WHEN une requête HTTP échoue avec une erreur serveur (status >= 500), THE Suite_de_Tests SHALL vérifier que le Routeur redirige vers la route "network-issue"
3. WHEN une requête HTTP échoue avec un status 401, THE Suite_de_Tests SHALL vérifier que le composable tente un rafraîchissement de token via /auth/refresh
4. WHEN le rafraîchissement de token échoue, THE Suite_de_Tests SHALL vérifier que le Store_Utilisateur déclenche un logout
5. WHEN une requête HTTP échoue, THE Suite_de_Tests SHALL vérifier que error contient le message d'erreur de la réponse API
6. WHEN sendRequest reçoit un FormData, THE Suite_de_Tests SHALL vérifier que le Content-Type n'est pas forcé à application/json

### Exigence 2 : Tests du composable useLazyLoad

**User Story :** En tant que développeur, je veux tester le composable useLazyLoad, afin de garantir le bon fonctionnement de la pagination, du tri et de la recherche avec debounce.

#### Critères d'acceptation

1. WHEN useLazyLoad est initialisé, THE Suite_de_Tests SHALL vérifier que lazyState contient les valeurs par défaut (first: 0, rows: 10, sortField: "nom", sortOrder: 1)
2. WHEN onLazyLoad est appelé avec un événement de pagination, THE Suite_de_Tests SHALL vérifier que lazyState est mis à jour avec les nouvelles valeurs first et rows
3. WHEN onSort est appelé, THE Suite_de_Tests SHALL vérifier que lazyState.first est réinitialisé à 0
4. WHEN search est modifié avec une valeur non vide, THE Suite_de_Tests SHALL vérifier qu'une requête de recherche est envoyée après un délai de 300ms (debounce)
5. WHEN onResetFilter est appelé, THE Suite_de_Tests SHALL vérifier que search est réinitialisé à une chaîne vide
6. WHEN getData est appelé, THE Suite_de_Tests SHALL vérifier que la requête HTTP contient les paramètres page, limit, field et order corrects

### Exigence 3 : Tests du composable useChambresList

**User Story :** En tant que développeur, je veux tester le composable useChambresList, afin de garantir le bon fonctionnement de la récupération et du filtrage des services/chambres.

#### Critères d'acceptation

1. WHEN getChambres est appelé, THE Suite_de_Tests SHALL vérifier qu'une requête GET est envoyée vers /chambres/services
2. WHEN search est appelé avec une requête, THE Suite_de_Tests SHALL vérifier que les suggestions et la liste sont filtrées par correspondance de préfixe (startsWith) insensible à la casse
3. WHEN search ne trouve aucun résultat, THE Suite_de_Tests SHALL vérifier que la liste affichée est réinitialisée à la liste initiale complète
4. WHEN searchBySelect est appelé avec une valeur, THE Suite_de_Tests SHALL vérifier que searchValue est mis à jour et que la liste est filtrée par correspondance exacte de préfixe
5. WHEN resetSearchValue est appelé, THE Suite_de_Tests SHALL vérifier que searchValue est réinitialisé à une chaîne vide
6. WHEN searchValue est vidé manuellement, THE Suite_de_Tests SHALL vérifier que la liste et les suggestions sont réinitialisées à la liste initiale

### Exigence 4 : Tests du composable useListPatients

**User Story :** En tant que développeur, je veux tester le composable useListPatients, afin de garantir le bon fonctionnement de la gestion de la liste des patients avec suppression et dialogue de confirmation.

#### Critères d'acceptation

1. WHEN showDeleteDialog est appelé avec un patient, THE Suite_de_Tests SHALL vérifier que selectedPatient est mis à jour et que dialogVisible passe à true
2. WHEN onCancel est appelé, THE Suite_de_Tests SHALL vérifier que selectedPatient est réinitialisé à null et que dialogVisible passe à false
3. WHEN onConfirm est appelé, THE Suite_de_Tests SHALL vérifier qu'une requête DELETE est envoyée avec l'ID du patient sélectionné et que le dialogue est fermé
4. WHEN onTrash supprime un patient avec succès, THE Suite_de_Tests SHALL vérifier qu'un toast de succès est affiché et que getData est rappelé pour rafraîchir la liste
5. WHEN une erreur survient lors de la suppression, THE Suite_de_Tests SHALL vérifier qu'un toast d'erreur est affiché

### Exigence 5 : Tests du composable usePatient

**User Story :** En tant que développeur, je veux tester le composable usePatient, afin de garantir la récupération correcte des données d'un patient.

#### Critères d'acceptation

1. WHEN usePatient est initialisé, THE Suite_de_Tests SHALL vérifier que detailPatient est null
2. WHEN fetchPatientData est appelé avec un ID valide, THE Suite_de_Tests SHALL vérifier qu'une requête GET est envoyée vers /patients/patients/detail/{id} et que detailPatient est mis à jour avec les données reçues

### Exigence 6 : Tests du composable usePatientForm

**User Story :** En tant que développeur, je veux tester le composable usePatientForm, afin de garantir la validation et la soumission correctes du formulaire patient.

#### Critères d'acceptation

1. WHEN usePatientForm est initialisé, THE Suite_de_Tests SHALL vérifier que civilites contient ["Monsieur", "Madame", "Autre"] et que isEditing est false
2. WHEN onCreatePatient est appelé avec des données valides, THE Suite_de_Tests SHALL vérifier qu'une requête POST est envoyée vers /patients/patients avec la date formatée correctement
3. WHEN la création de patient réussit, THE Suite_de_Tests SHALL vérifier qu'un toast de succès est affiché et que le Routeur navigue vers /patient/{id}
4. WHEN onUpdatePatient est appelé avec des données valides, THE Suite_de_Tests SHALL vérifier qu'une requête PUT est envoyée vers /patients/patients/{id} et que isEditing repasse à false
5. IF une erreur survient lors de la soumission, THEN THE Suite_de_Tests SHALL vérifier qu'un toast d'erreur est affiché

### Exigence 7 : Tests du composable useDocuments

**User Story :** En tant que développeur, je veux tester le composable useDocuments, afin de garantir la gestion correcte de la visibilité du dialogue et du succès de téléversement.

#### Critères d'acceptation

1. WHEN useDocuments est initialisé, THE Suite_de_Tests SHALL vérifier que visible est false
2. WHEN toggleVisible est appelé, THE Suite_de_Tests SHALL vérifier que visible bascule entre true et false
3. WHEN handleUploadSuccess est appelé avec un message et un patientId, THE Suite_de_Tests SHALL vérifier qu'un toast de succès est affiché et que refreshData est appelé avec le patientId

### Exigence 8 : Tests du composable useDocumentManagement

**User Story :** En tant que développeur, je veux tester le composable useDocumentManagement, afin de garantir la suppression correcte des documents.

#### Critères d'acceptation

1. WHEN useDocumentManagement est initialisé, THE Suite_de_Tests SHALL vérifier que visible est false et que documentToDelete est null
2. WHEN deleteDocument est appelé avec un ID et un callback, THE Suite_de_Tests SHALL vérifier qu'une requête DELETE est envoyée vers /patients/delete/documents/delete/{id}
3. WHEN la suppression réussit, THE Suite_de_Tests SHALL vérifier qu'un toast de succès est affiché, que le callback onSuccess est exécuté, et que documentToDelete est réinitialisé à null

### Exigence 9 : Tests du composable useUploadDocument

**User Story :** En tant que développeur, je veux tester le composable useUploadDocument, afin de garantir le bon fonctionnement du téléversement de documents.

#### Critères d'acceptation

1. WHEN useUploadDocument est initialisé, THE Suite_de_Tests SHALL vérifier que documentTypes contient 8 types de documents et que isValid est false
2. WHEN un fichier et un type de document sont sélectionnés, THE Suite_de_Tests SHALL vérifier que isValid passe à true
3. WHEN onSubmit est appelé avec un fichier et un type valides, THE Suite_de_Tests SHALL vérifier qu'une requête POST multipart/form-data est envoyée vers /patients/upload/documents/create/{patientId}
4. WHEN le téléversement réussit, THE Suite_de_Tests SHALL vérifier que les événements "refresh" et "update:visible" sont émis et que selectedFile et selectedDocumentType sont réinitialisés
5. IF une erreur survient lors du téléversement, THEN THE Suite_de_Tests SHALL vérifier qu'un toast d'erreur est affiché


### Exigence 10 : Tests des vues simples (LoginView, NotFound, NetworkIssue)

**User Story :** En tant que développeur, je veux tester les vues simples du frontend, afin de garantir leur rendu correct et leur navigation.

#### Critères d'acceptation

1. WHEN LoginView est montée, THE Suite_de_Tests SHALL vérifier que le composant LoginForm est rendu dans la page
2. WHEN NotFound est montée, THE Suite_de_Tests SHALL vérifier que le message d'erreur 404 est affiché et qu'un lien de retour à l'accueil est présent
3. WHEN NetworkIssue est montée, THE Suite_de_Tests SHALL vérifier que le message de problème serveur est affiché

### Exigence 11 : Tests des vues layout (AccueilLayout, ChambresLayout)

**User Story :** En tant que développeur, je veux tester les vues layout, afin de garantir qu'elles rendent correctement le RouterView enfant.

#### Critères d'acceptation

1. WHEN AccueilLayout est montée, THE Suite_de_Tests SHALL vérifier que le composant contient un élément RouterView
2. WHEN ChambresLayout est montée, THE Suite_de_Tests SHALL vérifier que le composant contient un élément RouterView

### Exigence 12 : Tests des vues métier (AccueilView, PatientView, AddPatientView, ChambresView, AdmissionView)

**User Story :** En tant que développeur, je veux tester les vues métier principales, afin de garantir leur rendu correct avec les composants enfants et les composables associés.

#### Critères d'acceptation

1. WHEN AccueilView est montée, THE Suite_de_Tests SHALL vérifier que les composants PageHeader et ListPatients sont rendus
2. WHEN PatientView est montée avec un ID de patient valide, THE Suite_de_Tests SHALL vérifier que fetchPatientData est appelé avec l'ID de la route et que les composants PatientDetail et DocumentsList sont rendus
3. WHEN AddPatientView est montée, THE Suite_de_Tests SHALL vérifier que les composants PatientForm et PatientDataDisclaimer sont rendus
4. WHEN ChambresView est montée, THE Suite_de_Tests SHALL vérifier que le composant PageHeader est rendu et que la barre de recherche AutoComplete est présente
5. WHEN AdmissionView est montée, THE Suite_de_Tests SHALL vérifier que le formulaire d'admission avec les champs date d'entrée, date de sortie, ambulatoire et services est rendu

### Exigence 13 : Tests du store utilisateur

**User Story :** En tant que développeur, je veux tester le store Pinia user, afin de garantir la gestion correcte de l'authentification et des préférences utilisateur.

#### Critères d'acceptation

1. WHEN le Store_Utilisateur est initialisé, THE Suite_de_Tests SHALL vérifier que role est une chaîne vide, mode est "light" et authChecked est false
2. WHEN getUserInfos est appelé avec succès, THE Suite_de_Tests SHALL vérifier que role est mis à jour avec la valeur retournée par l'API et que authChecked passe à true
3. WHEN getUserInfos échoue, THE Suite_de_Tests SHALL vérifier que authChecked passe à true malgré l'erreur
4. WHEN signout est appelé, THE Suite_de_Tests SHALL vérifier que role est réinitialisé à une chaîne vide et qu'une requête POST est envoyée vers /auth/logout
5. WHEN logout est appelé, THE Suite_de_Tests SHALL vérifier que role est réinitialisé à une chaîne vide et que le Routeur redirige vers la route racine

### Exigence 14 : Tests du routeur

**User Story :** En tant que développeur, je veux tester la configuration du routeur, afin de garantir la protection des routes par rôle et les redirections correctes.

#### Critères d'acceptation

1. WHEN un utilisateur non authentifié accède à la route racine "/", THE Suite_de_Tests SHALL vérifier que LoginView est affichée
2. WHEN un utilisateur avec le rôle "home" accède à la route racine "/", THE Suite_de_Tests SHALL vérifier que le Routeur redirige vers /accueil
3. WHEN un utilisateur sans le rôle "home" accède à /accueil, THE Suite_de_Tests SHALL vérifier que le Routeur redirige vers la route racine "/"
4. WHEN un utilisateur accède à une route inexistante, THE Suite_de_Tests SHALL vérifier que la vue NotFound est affichée
5. WHEN un utilisateur avec un rôle autorisé (home, nurses, cleaning) accède à /chambres, THE Suite_de_Tests SHALL vérifier que l'accès est autorisé

### Exigence 15 : Tests des utilitaires (regex, urls, services)

**User Story :** En tant que développeur, je veux tester les modules utilitaires, afin de garantir la fiabilité des expressions régulières et des constantes de configuration.

#### Critères d'acceptation

1. THE Suite_de_Tests SHALL vérifier que regexMail accepte les adresses email valides et rejette les adresses invalides
2. THE Suite_de_Tests SHALL vérifier que regexPassword accepte les mots de passe conformes (12+ caractères, majuscule, minuscule, chiffre, caractère spécial) et rejette les mots de passe non conformes
3. THE Suite_de_Tests SHALL vérifier que regexGeneric accepte les chaînes alphanumériques avec caractères accentués et rejette les chaînes contenant des caractères interdits
