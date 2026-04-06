# Tâches d'implémentation

## Tâches

- [x] 1. Remplacer les appels `localStorage.clear()` dans `UserStore.spec.ts`
  - [x] 1.1 Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')` dans le `beforeEach` du bloc `toggleColorScheme`
  - [x] 1.2 Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')` dans le `beforeEach` du bloc `updateColorScheme`
  - [x] 1.3 Remplacer `localStorage.clear()` par `localStorage.removeItem('color-scheme')` dans le `beforeEach` du bloc `handshake`
- [x] 2. Vérifier que tous les tests passent
  - [x] 2.1 Exécuter `vitest --run` pour confirmer que les 14 tests de `UserStore.spec.ts` passent sans erreur
