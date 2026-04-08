# Correction du Bug localStorage.clear() en CI — Design

## Overview

Le fichier de test `UserStore.spec.ts` échoue en CI Jenkins avec `TypeError: localStorage.clear is not a function`. L'implémentation de `localStorage` fournie par `happy-dom` dans l'environnement Node.js de Jenkins ne supporte pas la méthode `clear()`. Le correctif consiste à remplacer les 3 appels `localStorage.clear()` dans les blocs `beforeEach` par `localStorage.removeItem('color-scheme')`, qui est la seule clé utilisée par le store et qui est une méthode standard supportée par toutes les implémentations de `Storage`.

## Glossaire

- **Bug_Condition (C)** : L'appel à `localStorage.clear()` dans un environnement où `happy-dom` ne fournit pas cette méthode (CI Jenkins)
- **Property (P)** : Le nettoyage du localStorage dans les `beforeEach` doit fonctionner sans erreur dans tous les environnements
- **Preservation** : Les 5 tests impactés doivent continuer à passer, ainsi que tous les autres tests non liés au localStorage
- **`localStorage.clear()`** : Méthode standard de l'API Web Storage qui supprime toutes les entrées — non disponible dans certaines implémentations `happy-dom`
- **`localStorage.removeItem(key)`** : Méthode standard de l'API Web Storage qui supprime une entrée spécifique — supportée par toutes les implémentations
- **`happy-dom`** : Environnement DOM simulé utilisé par Vitest, configuré dans `vitest.config.ts`

## Bug Details

### Bug Condition

Le bug se manifeste quand les blocs `beforeEach` des sections `toggleColorScheme`, `updateColorScheme` et `handshake` appellent `localStorage.clear()` dans l'environnement `happy-dom` du serveur Jenkins CI. La méthode `clear()` n'est pas disponible sur l'objet `localStorage` dans cette configuration spécifique.

**Spécification formelle :**
```
FUNCTION isBugCondition(input)
  INPUT: input de type { testBlock: string, environment: string, nodeVersion: string }
  OUTPUT: boolean

  RETURN input.testBlock IN ['toggleColorScheme', 'updateColorScheme', 'handshake']
         AND input.environment == 'happy-dom'
         AND typeof localStorage.clear !== 'function'
END FUNCTION
```

### Exemples

- `toggleColorScheme` beforeEach : appelle `localStorage.clear()` → `TypeError: localStorage.clear is not a function` en CI, passe en local
- `updateColorScheme` beforeEach : appelle `localStorage.clear()` → `TypeError: localStorage.clear is not a function` en CI, passe en local
- `handshake` beforeEach : appelle `localStorage.clear()` → `TypeError: localStorage.clear is not a function` en CI, passe en local
- `initial state` / `signout` / `logout` : n'appellent pas `localStorage.clear()` → passent en CI et en local (non impactés)

## Expected Behavior

### Preservation Requirements

**Comportements inchangés :**
- Les appels `localStorage.setItem('color-scheme', 'dark')` dans les tests doivent continuer à fonctionner
- Les appels `localStorage.getItem('color-scheme')` dans les tests doivent continuer à retourner les valeurs correctes
- Les appels `localStorage.removeItem('color-scheme')` dans le store `user.ts` doivent continuer à fonctionner
- Les tests `initial state`, `getUserInfos success`, `getUserInfos failure`, `signout` et `logout` doivent continuer à passer sans modification
- Les tests doivent continuer à passer en local avec `happy-dom`

**Portée :**
Seuls les 3 appels `localStorage.clear()` dans les blocs `beforeEach` sont modifiés. Aucun autre code n'est touché. Les inputs suivants ne sont pas affectés :
- Tous les appels `localStorage.setItem()` / `localStorage.getItem()` / `localStorage.removeItem()` existants
- Le code du store `user.ts` (aucune modification)
- La configuration Vitest (`vitest.config.ts`)

## Hypothesized Root Cause

D'après l'analyse du bug, la cause la plus probable est :

1. **Incompatibilité `happy-dom` / Node.js** : L'implémentation de `localStorage` par `happy-dom` varie selon la version de Node.js. Sur le serveur Jenkins, la version de Node.js ou de `happy-dom` ne fournit pas `localStorage.clear()` comme méthode de l'objet Storage simulé.

2. **Utilisation inutile de `clear()`** : Le test n'utilise qu'une seule clé (`color-scheme`) dans le localStorage. L'appel à `clear()` est excessif — `removeItem('color-scheme')` suffit et est garanti par toutes les implémentations de Storage.

3. **Différence d'environnement local vs CI** : En local, une version plus récente de `happy-dom` ou de Node.js peut fournir `clear()`, masquant le problème qui n'apparaît qu'en CI.

## Correctness Properties

Property 1: Bug Condition — Le nettoyage du localStorage ne lève pas d'erreur

_Pour tout_ bloc `beforeEach` des sections `toggleColorScheme`, `updateColorScheme` et `handshake`, la méthode de nettoyage du localStorage SHALL s'exécuter sans lever de `TypeError` dans tous les environnements (local et CI), et le localStorage SHALL ne plus contenir la clé `color-scheme` après le nettoyage.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation — Les opérations localStorage standard continuent de fonctionner

_Pour tout_ test qui utilise `localStorage.setItem()`, `localStorage.getItem()` ou `localStorage.removeItem()`, le comportement SHALL rester identique après le correctif. Les tests non liés au localStorage (`initial state`, `getUserInfos`, `signout`, `logout`) SHALL continuer à passer sans régression.

**Validates: Requirements 3.1, 3.2, 3.3**

## Fix Implementation

### Changes Required

En supposant que notre analyse de la cause racine est correcte :

**Fichier** : `cmv_gateway/cmv_front/src/tests/UserStore.spec.ts`

**Changements spécifiques** :

1. **Remplacement dans `toggleColorScheme` beforeEach** (ligne ~155) :
   - Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')`

2. **Remplacement dans `updateColorScheme` beforeEach** (ligne ~178) :
   - Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')`

3. **Remplacement dans `handshake` beforeEach** (ligne ~200) :
   - Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')`

**Aucune autre modification requise** — le store `user.ts` et la configuration Vitest restent inchangés.

## Testing Strategy

### Validation Approach

La stratégie de test suit une approche en deux phases : d'abord, confirmer que le bug existe sur le code non corrigé, puis vérifier que le correctif fonctionne et préserve le comportement existant.

### Exploratory Bug Condition Checking

**Objectif** : Confirmer que `localStorage.clear()` provoque bien l'erreur dans l'environnement CI et comprendre la cause racine.

**Plan de test** : Exécuter les tests non corrigés dans un environnement similaire à Jenkins pour observer les échecs.

**Cas de test** :
1. **Test toggleColorScheme** : Exécuter le beforeEach avec `localStorage.clear()` (échouera en CI)
2. **Test updateColorScheme** : Exécuter le beforeEach avec `localStorage.clear()` (échouera en CI)
3. **Test handshake** : Exécuter le beforeEach avec `localStorage.clear()` (échouera en CI)

**Contre-exemples attendus** :
- `TypeError: localStorage.clear is not a function` dans chaque beforeEach
- Cause : `happy-dom` ne fournit pas `clear()` dans l'environnement Node.js de Jenkins

### Fix Checking

**Objectif** : Vérifier que pour tous les blocs `beforeEach` impactés, le nettoyage via `removeItem` fonctionne sans erreur.

**Pseudocode :**
```
FOR ALL testBlock WHERE isBugCondition(testBlock) DO
  result := executeBeforeEach_fixed(testBlock)
  ASSERT result.noError == true
  ASSERT localStorage.getItem('color-scheme') == null
END FOR
```

### Preservation Checking

**Objectif** : Vérifier que tous les tests non impactés continuent de passer et que les opérations localStorage standard fonctionnent.

**Pseudocode :**
```
FOR ALL testBlock WHERE NOT isBugCondition(testBlock) DO
  ASSERT executeTest_original(testBlock) == executeTest_fixed(testBlock)
END FOR
```

**Approche de test** : Les tests property-based sont recommandés pour la vérification de préservation car :
- Ils génèrent automatiquement de nombreux cas de test sur le domaine d'entrée
- Ils détectent les cas limites que les tests unitaires manuels pourraient manquer
- Ils fournissent des garanties solides que le comportement est inchangé pour tous les inputs non bugués

**Plan de test** : Observer le comportement sur le code non corrigé pour les opérations localStorage standard, puis écrire des tests property-based capturant ce comportement.

**Cas de test** :
1. **Préservation setItem/getItem** : Vérifier que `localStorage.setItem('color-scheme', 'dark')` suivi de `localStorage.getItem('color-scheme')` retourne `'dark'` après le fix
2. **Préservation removeItem** : Vérifier que `localStorage.removeItem('color-scheme')` supprime bien la clé après le fix
3. **Préservation des tests non liés** : Vérifier que les tests `initial state`, `getUserInfos`, `signout`, `logout` passent sans modification

### Unit Tests

- Vérifier que `localStorage.removeItem('color-scheme')` nettoie correctement le localStorage dans chaque beforeEach
- Vérifier que les 5 tests impactés passent après le correctif
- Vérifier que les tests non impactés continuent de passer

### Property-Based Tests

- Générer des états aléatoires du localStorage et vérifier que `removeItem('color-scheme')` supprime toujours la clé sans erreur
- Vérifier que pour toute valeur stockée dans `color-scheme`, le nettoyage via `removeItem` produit un état propre

### Integration Tests

- Exécuter la suite complète de tests `UserStore.spec.ts` et vérifier que tous les 14 tests passent
- Vérifier que le pipeline CI Jenkins passe sans erreur après le correctif
