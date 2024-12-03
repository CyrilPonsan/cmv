/**
 * Série de tests pour la fonctionnalité de recherche de patients
 */

import useLazyLoad from '@/composables/useLazyLoad'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'

// Mock useHttp
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: vi.fn(),
    isLoading: ref(false)
  })
}))

describe('useLazyLoad composable', () => {
  let composable: ReturnType<typeof useLazyLoad<any>>

  beforeEach(() => {
    setActivePinia(createPinia())
    composable = useLazyLoad<any>('/api/patients')
  })

  it('should update search value and reset pagination', () => {
    composable.search.value = 'test'

    expect(composable.lazyState.value.first).toBe(0)
    expect(composable.loading.value).toBe(false)
  })

  it('should reset search value', () => {
    composable.search.value = 'test'
    composable.onResetFilter()

    expect(composable.search.value).toBe('')
    expect(composable.lazyState.value.first).toBe(0)
  })
})
