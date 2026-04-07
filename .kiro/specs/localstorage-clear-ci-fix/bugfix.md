# Document de Correction de Bug

## Introduction

Le fichier de test `cmv_gateway/cmv_front/src/tests/UserStore.spec.ts` échoue dans le pipeline Jenkins CI avec l'erreur `TypeError: localStorage.clear is not a function`. L'erreur survient dans les blocs `beforeEach` des sections `toggleColorScheme`, `updateColorScheme` et `handshake` qui appellent `localStorage.clear()`. Les tests passent en local mais échouent en CI car l'implémentation de `localStorage` fournie par `happy-dom` ne garantit pas la disponibilité de la méthode `clear()` dans tous les environnements Node.js (notamment celui utilisé par Jenkins). 5 tests sont impactés.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN les tests `toggleColorScheme`, `updateColorScheme` et `handshake` sont exécutés dans le pipeline Jenkins CI THEN le système échoue avec `TypeError: localStorage.clear is not a function` dans les blocs `beforeEach` (lignes ~220, ~231, ~238)

1.2 WHEN `localStorage.clear()` est appelé dans l'environnement `happy-dom` sous la version Node.js du serveur Jenkins THEN la méthode `clear()` n'est pas disponible sur l'objet `localStorage`, provoquant un crash des 5 tests concernés

### Expected Behavior (Correct)

2.1 WHEN les tests `toggleColorScheme`, `updateColorScheme` et `handshake` sont exécutés dans le pipeline Jenkins CI THEN le système SHALL nettoyer le `localStorage` sans erreur et les 5 tests SHALL passer avec succès

2.2 WHEN le nettoyage du `localStorage` est effectué dans le `beforeEach` sous n'importe quel environnement (local ou CI) THEN le système SHALL utiliser une méthode de nettoyage compatible avec toutes les implémentations de `Storage` (par exemple, supprimer les clés individuellement ou réassigner le storage) au lieu de dépendre de `localStorage.clear()`

### Unchanged Behavior (Regression Prevention)

3.1 WHEN les tests `initial state`, `getUserInfos success`, `getUserInfos failure`, `signout` et `logout` sont exécutés THEN le système SHALL CONTINUE TO les exécuter avec succès sans régression

3.2 WHEN `localStorage.setItem()`, `localStorage.getItem()` et `localStorage.removeItem()` sont appelés dans les tests THEN le système SHALL CONTINUE TO fonctionner correctement pour la lecture et l'écriture des préférences de thème (`color-scheme`)

3.3 WHEN les tests sont exécutés en local avec `happy-dom` THEN le système SHALL CONTINUE TO passer tous les tests sans régression
