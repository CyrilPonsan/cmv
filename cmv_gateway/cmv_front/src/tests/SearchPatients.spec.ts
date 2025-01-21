/**
 * Série de tests pour la fonctionnalité de recherche de patients
 */

import useLazyLoad from '@/composables/useLazyLoad'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'

// Mock du composable useHttp pour simuler les appels API
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: vi.fn(), // Mock de la fonction d'envoi de requête
    isLoading: ref(false) // État de chargement initial
  })
}))

describe('useLazyLoad composable', () => {
  // Déclaration du type pour le composable qui sera testé
  let composable: ReturnType<typeof useLazyLoad<any>>

  // Avant chaque test, on réinitialise le store Pinia et le composable
  beforeEach(() => {
    setActivePinia(createPinia())
    composable = useLazyLoad<any>('/api/patients')
  })

  // Test de la mise à jour de la valeur de recherche et réinitialisation de la pagination
  it('should update search value and reset pagination', () => {
    // Définition d'une valeur de recherche
    composable.search.value = 'test'

    // Vérification que la pagination est réinitialisée à 0
    expect(composable.lazyState.value.first).toBe(0)
    // Vérification que l'état de chargement est false
    expect(composable.loading.value).toBe(false)
  })

  // Test de la réinitialisation du filtre de recherche
  it('should reset search value', () => {
    // Définition d'une valeur de recherche
    composable.search.value = 'test'
    // Appel de la fonction de réinitialisation
    composable.onResetFilter()

    // Vérification que la valeur de recherche est vide
    expect(composable.search.value).toBe('')
    // Vérification que la pagination est réinitialisée à 0
    expect(composable.lazyState.value.first).toBe(0)
  })
})
