# Document de Conception — Couverture de Tests Frontend

## Vue d'ensemble

Ce document décrit l'architecture et la stratégie de test pour étendre la couverture de tests unitaires du frontend Vue.js du projet CMV Healthcare. L'objectif est de couvrir les composables non testés (useHttp, useLazyLoad, useChambresList, useListPatients, usePatient, usePatientForm, useDocuments, useDocumentManagement, useUploadDocument), les vues (LoginView, NotFound, NetworkIssue, AccueilLayout, ChambresLayout, AccueilView, PatientView, AddPatientView, ChambresView, AdmissionView), le store Pinia utilisateur, le routeur avec ses gardes de rôle, et les utilitaires regex.

La pile de test repose sur Vitest (runner), @vue/test-utils (montage de composants Vue), happy-dom (environnement DOM), @pinia/testing (mock du store), et fast-check (tests property-based). Tous les fichiers de test sont placés dans `cmv_gateway/cmv_front/src/tests/`.

## Architecture

```mermaid
graph TD
    subgraph "Environnement de Test"
        V[Vitest + happy-dom]
        VTU[@vue/test-utils]
        PT[@pinia/testing]
        FC[fast-check]
    end

    subgraph "Couche Mocks"
        MA[axios mock]
        MR[vue-router mock]
        MT[useToast mock]
        MI[vue-i18n mock]
        MP[PrimeVue components mock]
    end

    subgraph "Sujets de Test"
        C[Composables]
        VW[Vues]
        S[Store Pinia]
        R[Routeur]
        U[Utilitaires]
    end

    V --> VTU
    V --> PT
    V --> FC
    VTU --> MP
    C --> MA
    C --> MT
    C --> MI
    S --> MA
    S --> MR
    R --> PT
    VW --> VTU
    U --> FC
```

### Principes architecturaux

1. **Isolation complète** : chaque test mocke ses dépendances externes (HTTP, router, toast, i18n)
2. **Convention de nommage** : `{NomDuModule}.spec.ts` dans `src/tests/`
3. **Pas de serveur réel** : toutes les requêtes HTTP sont interceptées via des mocks axios
4. **Réactivité testée** : les refs Vue sont vérifiées avant/après les actions
5. **Cohérence avec l'existant** : les nouveaux tests suivent les patterns de `LoginForm.spec.ts` et `UseLogin.spec.ts`

## Composants et Interfaces

### Stratégie de mock par type de dépendance

#### 1. HTTP (axios via useHttp)

Pour les composables qui utilisent `useHttp` directement, deux approches :

- **Mock du module useHttp** : `vi.mock('@/composables/useHttp')` retournant `{ sendRequest: vi.fn(), isLoading: ref(false), error: ref(null) }`. Utilisé pour les composables de haut niveau (useListPatients, usePatient, usePatientForm, useChambresList, useDocumentManagement, useUploadDocument).
- **Mock d'axios** : `vi.mock('axios')` avec une instance mockée. Utilisé pour tester useHttp lui-même (intercepteurs, refresh token, gestion d'erreurs).

```typescript
// Pattern mock useHttp
const mockSendRequest = vi.fn()
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: ref(null),
    axiosInstance: {}
  })
}))
```

#### 2. Router (vue-router)

```typescript
const mockPush = vi.fn()
const mockRoute = { params: { id: '1' }, name: 'patient' }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush, back: vi.fn() }),
  useRoute: () => mockRoute,
  createRouter: vi.fn(),
  createWebHistory: vi.fn()
}))
```

#### 3. Store Pinia (useUserStore)

Deux approches selon le contexte :
- **@pinia/testing** : `createTestingPinia({ createSpy: vi.fn })` pour les tests de vues
- **Mock direct** : `vi.mock('@/stores/user')` pour les tests de composables

```typescript
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    role: 'home',
    getUserInfos: vi.fn(),
    logout: vi.fn(),
    signout: vi.fn()
  })
}))
```

#### 4. Toast (PrimeVue useToast)

```typescript
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: mockToastAdd })
}))
```

#### 5. i18n (vue-i18n)

```typescript
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))
```

#### 6. Composants PrimeVue

Les composants PrimeVue (Button, InputText, AutoComplete, DatePicker, Select, etc.) sont mockés avec des templates HTML simples, comme dans les tests existants.

### Organisation des fichiers de test

```
cmv_gateway/cmv_front/src/tests/
├── UseHttp.spec.ts              # Exigence 1
├── UseLazyLoad.spec.ts          # Exigence 2
├── UseChambresList.spec.ts      # Exigence 3
├── UseListPatients.spec.ts      # Exigence 4
├── UsePatient.spec.ts           # Exigence 5
├── UsePatientForm.spec.ts       # Exigence 6
├── UseDocuments.spec.ts         # Exigence 7
├── UseDocumentManagement.spec.ts # Exigence 8
├── UseUploadDocument.spec.ts    # Exigence 9
├── SimpleViews.spec.ts          # Exigence 10
├── LayoutViews.spec.ts          # Exigence 11
├── BusinessViews.spec.ts        # Exigence 12
├── UserStore.spec.ts            # Exigence 13
├── Router.spec.ts               # Exigence 14
├── Regex.spec.ts                # Exigence 15 (unit + property)
├── LoginForm.spec.ts            # (existant)
├── UseLogin.spec.ts             # (existant)
└── ...                          # (autres existants)
```

### Détail des implémentations par composable

#### UseHttp.spec.ts
- Mock axios au niveau module avec `vi.mock('axios')`
- Simule les réponses réussies, erreurs 401, erreurs 500, échec de refresh
- Vérifie les transitions de `isLoading` et le contenu de `error`
- Vérifie la détection automatique de FormData pour le Content-Type

#### UseLazyLoad.spec.ts
- Mock useHttp pour intercepter les appels `sendRequest`
- Vérifie les valeurs par défaut de `lazyState`
- Simule les événements de pagination et de tri
- Utilise `vi.useFakeTimers()` pour tester le debounce de 300ms sur la recherche

#### UseChambresList.spec.ts
- Mock useHttp pour simuler les réponses de `/chambres/services`
- Teste le filtrage par préfixe (startsWith) insensible à la casse
- Vérifie la réinitialisation de la liste quand la recherche est vide

#### UseListPatients.spec.ts
- Mock useHttp et useLazyLoad
- Teste le cycle complet du dialogue de suppression (show → cancel/confirm)
- Vérifie l'appel DELETE et le toast de succès/erreur

#### UsePatient.spec.ts
- Mock useHttp
- Vérifie que `detailPatient` est null à l'initialisation
- Vérifie l'appel GET vers `/patients/patients/detail/{id}`

#### UsePatientForm.spec.ts
- Mock useHttp, vue-router, useToast
- Teste la validation Zod du schéma
- Vérifie le formatage de la date (ajout de 12h)
- Teste la navigation après création réussie

#### UseDocuments.spec.ts
- Mock useToast et useI18n
- Teste le toggle de visibilité
- Vérifie l'appel du callback refreshData et du toast

#### UseDocumentManagement.spec.ts
- Mock useHttp et useToast
- Teste la suppression avec callback onSuccess
- Vérifie la réinitialisation de documentToDelete

#### UseUploadDocument.spec.ts
- Mock useHttp et useToast
- Vérifie les 8 types de documents
- Teste la validation isValid (fichier + type requis)
- Vérifie la construction du FormData et les émissions d'événements

## Modèles de Données

### Structures de données utilisées dans les tests

```typescript
// Patient simplifié pour les tests de liste
interface PatientsListItem {
  id_patient: number
  nom: string
  prenom: string
  date_de_naissance: string
}

// Patient détaillé pour les tests de vue patient
interface DetailPatient {
  id_patient: number
  nom: string
  prenom: string
  civilite: string
  date_de_naissance: string
  adresse: string
  code_postal: string
  ville: string
  telephone: string
  email?: string
  documents: Document[]
  latest_admission?: Admission
}

// Document pour les tests de gestion documentaire
interface Document {
  id_document: number
  document_type: string
  filename: string
  created_at: string
}

// Service/Chambre pour les tests de chambres
interface Service {
  id_service: number
  nom: string
  chambres: Chambre[]
}

// Réponse API paginée
interface APIResponse<T> {
  data: T[]
  total: number
}

// Réponse API avec message
interface SuccessWithMessage {
  success: boolean
  message: string
}

// Credentials pour les tests de login
interface Credentials {
  username: string
  password: string
}
```

### Données de test (fixtures)

Les tests utilisent des factories simples pour générer des données :

```typescript
const createMockPatient = (overrides = {}): PatientsListItem => ({
  id_patient: 1,
  nom: 'Dupont',
  prenom: 'Jean',
  date_de_naissance: '1990-01-15',
  ...overrides
})

const createMockService = (overrides = {}): Service => ({
  id_service: 1,
  nom: 'Cardiologie',
  chambres: [],
  ...overrides
})
```


## Propriétés de Correction

*Une propriété est une caractéristique ou un comportement qui doit rester vrai pour toutes les exécutions valides d'un système — essentiellement, une déclaration formelle de ce que le système doit faire. Les propriétés servent de pont entre les spécifications lisibles par l'humain et les garanties de correction vérifiables par la machine.*

### Propriété 1 : Transition isLoading sur requête réussie

*Pour toute* donnée de réponse HTTP valide, lorsque `sendRequest` est appelé et que la requête réussit, `isLoading` doit passer à `true` pendant la requête puis revenir à `false` après résolution, et les données retournées doivent correspondre à la réponse.

**Valide : Exigences 1.1**

### Propriété 2 : Redirection sur erreur serveur

*Pour tout* code de statut HTTP >= 500, lorsque `sendRequest` reçoit une réponse avec ce statut, le routeur doit être appelé avec la route "network-issue".

**Valide : Exigences 1.2**

### Propriété 3 : Capture du message d'erreur API

*Pour toute* réponse HTTP en erreur contenant un champ `detail`, la ref `error` du composable useHttp doit contenir exactement la valeur de ce champ `detail`.

**Valide : Exigences 1.5**

### Propriété 4 : Mise à jour de lazyState par pagination

*Pour tout* événement de pagination contenant des valeurs `first` et `rows` arbitraires, après appel de `onLazyLoad`, `lazyState.first` et `lazyState.rows` doivent correspondre exactement aux valeurs de l'événement.

**Valide : Exigences 2.2**

### Propriété 5 : Réinitialisation de first lors du tri

*Pour tout* état de `lazyState` avec un `first` non nul, lorsque `onSort` est appelé, `lazyState.first` doit être réinitialisé à 0.

**Valide : Exigences 2.3**

### Propriété 6 : Construction correcte des paramètres URL de getData

*Pour toute* configuration de `lazyState` (first, rows, sortField, sortOrder), l'URL construite par `getData` doit contenir les paramètres `page`, `limit`, `field` et `order` calculés correctement (page = first/rows + 1, order = "asc" si sortOrder=1 sinon "desc").

**Valide : Exigences 2.6**

### Propriété 7 : Filtrage par préfixe des services

*Pour toute* liste de services et toute chaîne de recherche, le filtrage (via `search` ou `searchBySelect`) doit retourner uniquement des services dont le nom commence par la chaîne de recherche (comparaison insensible à la casse pour `search`, sensible pour `searchBySelect`).

**Valide : Exigences 3.2, 3.4**

### Propriété 8 : showDeleteDialog met à jour l'état du dialogue

*Pour tout* objet patient, après appel de `showDeleteDialog(patient)`, `selectedPatient` doit être égal au patient fourni et `dialogVisible` doit être `true`.

**Valide : Exigences 4.1**

### Propriété 9 : Construction de l'URL fetchPatientData

*Pour tout* identifiant de patient (nombre entier positif), l'appel à `fetchPatientData(id)` doit déclencher une requête vers `/patients/patients/detail/{id}`.

**Valide : Exigences 5.2**

### Propriété 10 : Formatage de la date à midi lors de la création patient

*Pour toute* date de naissance valide, lorsque `onCreatePatient` est appelé, la date envoyée dans la requête doit avoir les heures fixées à 12, les minutes à 0 et les secondes à 0, tout en conservant l'année, le mois et le jour d'origine.

**Valide : Exigences 6.2**

### Propriété 11 : Idempotence du double toggle de visibilité

*Pour tout* état initial de `visible`, appeler `toggleVisible` deux fois doit ramener `visible` à sa valeur initiale.

**Valide : Exigences 7.2**

### Propriété 12 : Construction de l'URL de suppression de document

*Pour tout* identifiant de document (nombre entier positif), l'appel à `deleteDocument(id, callback)` doit déclencher une requête DELETE vers `/patients/delete/documents/delete/{id}`.

**Valide : Exigences 8.2**

### Propriété 13 : Validité du formulaire d'upload

*Pour tout* fichier non null et tout type de document non null, `isValid` doit être `true`. *Pour tout* état où le fichier est null OU le type est null, `isValid` doit être `false`.

**Valide : Exigences 9.2**

### Propriété 14 : Routes inexistantes affichent NotFound

*Pour tout* chemin URL ne correspondant à aucune route définie ("/", "/accueil", "/patient/:id", "/add-patient", "/chambres", "/admissions/create/:patientId"), le routeur doit résoudre vers le composant NotFound.

**Valide : Exigences 14.4**

### Propriété 15 : Accès aux chambres par rôles autorisés

*Pour tout* rôle dans l'ensemble {"home", "nurses", "cleaning"}, l'accès à la route `/chambres` doit être autorisé. *Pour tout* rôle en dehors de cet ensemble, l'accès doit être refusé avec redirection vers "/".

**Valide : Exigences 14.5**

### Propriété 16 : Validation regex email

*Pour toute* chaîne respectant le format `local@domain.tld` (partie locale sans caractères interdits, domaine avec au moins un point et un TLD de 2+ caractères), `regexMail` doit retourner un match. *Pour toute* chaîne ne respectant pas ce format, `regexMail` ne doit pas matcher.

**Valide : Exigences 15.1**

### Propriété 17 : Validation regex mot de passe

*Pour toute* chaîne de 12+ caractères contenant au moins une minuscule, une majuscule, un chiffre et un caractère spécial parmi `-!@#$%^&*`, et ne contenant pas `<>"'`, `regexPassword` doit retourner un match. *Pour toute* chaîne ne respectant pas l'un de ces critères, `regexPassword` ne doit pas matcher.

**Valide : Exigences 15.2**

### Propriété 18 : Validation regex générique

*Pour toute* chaîne non vide composée uniquement de caractères alphanumériques, espaces, virgules, points, apostrophes, tirets, plus, accents français (éàèîâôêûù), points d'interrogation, points d'exclamation, slashes, underscores et parenthèses, `regexGeneric` doit retourner un match.

**Valide : Exigences 15.3**

## Gestion des Erreurs

### Stratégie de gestion des erreurs dans les tests

| Scénario | Comportement attendu | Test |
|---|---|---|
| Erreur réseau (pas de réponse) | `error` contient "unknown_error" | UseHttp.spec.ts |
| Erreur serveur (5xx) | Redirection vers "network-issue" | UseHttp.spec.ts |
| Erreur 401 | Tentative de refresh token | UseHttp.spec.ts |
| Refresh token échoue | Appel `userStore.logout()` | UseHttp.spec.ts |
| Erreur API avec `detail` | `error.value` = `response.data.detail` | UseHttp.spec.ts |
| Suppression patient échoue | Toast d'erreur affiché | UseListPatients.spec.ts |
| Création patient échoue | Toast d'erreur affiché | UsePatientForm.spec.ts |
| Upload document échoue | Toast d'erreur affiché | UseUploadDocument.spec.ts |

### Patterns de test d'erreur

```typescript
// Pattern : simuler une erreur HTTP et vérifier le comportement
it('should display error toast on failure', async () => {
  mockSendRequest.mockImplementation((req, applyData) => {
    // Ne pas appeler applyData — simuler une erreur
    throw { response: { data: { detail: 'error_message' } } }
  })
  // ... déclencher l'action
  // ... vérifier le toast d'erreur
})
```

## Stratégie de Test

### Approche duale

Les tests sont organisés en deux catégories complémentaires :

1. **Tests unitaires** (Vitest + @vue/test-utils) : vérifient des exemples concrets, des cas limites et des conditions d'erreur. Ils couvrent la majorité des critères d'acceptation (états initiaux, scénarios de succès/erreur, rendu de composants).

2. **Tests property-based** (fast-check) : vérifient les propriétés universelles sur des entrées générées aléatoirement. Ils couvrent les propriétés 1-18 définies ci-dessus.

### Bibliothèque property-based

- **Bibliothèque** : `fast-check` (à installer via `npm install -D fast-check`)
- **Configuration** : minimum 100 itérations par test property-based
- **Intégration** : fast-check s'intègre nativement avec Vitest via `fc.assert(fc.property(...))`

### Convention de tagging des tests property-based

Chaque test property-based doit inclure un commentaire de référence :

```typescript
// Feature: frontend-test-coverage, Property 16: Validation regex email
it('should match valid emails', () => {
  fc.assert(
    fc.property(fc.emailAddress(), (email) => {
      expect(regexMail.test(email)).toBe(true)
    }),
    { numRuns: 100 }
  )
})
```

### Répartition tests unitaires vs property-based

| Fichier de test | Tests unitaires | Tests property-based |
|---|---|---|
| UseHttp.spec.ts | 401 refresh, FormData, logout | Propriétés 1, 2, 3 |
| UseLazyLoad.spec.ts | Valeurs par défaut, debounce, reset | Propriétés 4, 5, 6 |
| UseChambresList.spec.ts | getChambres endpoint, reset, empty search | Propriété 7 |
| UseListPatients.spec.ts | Cancel, confirm, trash success/error | Propriété 8 |
| UsePatient.spec.ts | État initial null | Propriété 9 |
| UsePatientForm.spec.ts | Initialisation, succès création, update, erreur | Propriété 10 |
| UseDocuments.spec.ts | État initial, handleUploadSuccess | Propriété 11 |
| UseDocumentManagement.spec.ts | État initial, succès suppression | Propriété 12 |
| UseUploadDocument.spec.ts | 8 types, submit, events, erreur | Propriété 13 |
| SimpleViews.spec.ts | Rendu LoginView, NotFound, NetworkIssue | — |
| LayoutViews.spec.ts | RouterView dans layouts | — |
| BusinessViews.spec.ts | Rendu composants enfants | — |
| UserStore.spec.ts | Init, getUserInfos, signout, logout | — |
| Router.spec.ts | Auth redirect, role guard | Propriétés 14, 15 |
| Regex.spec.ts | Exemples concrets valides/invalides | Propriétés 16, 17, 18 |

### Exécution

```bash
# Lancer tous les tests unitaires
cd cmv_gateway/cmv_front && npx vitest --run

# Lancer un fichier spécifique
npx vitest --run src/tests/UseHttp.spec.ts
```
