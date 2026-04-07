import { describe, it, expect, vi, beforeEach } from 'vitest'

// --- Mock PrimeVue useToast ---
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: mockToastAdd })
}))

// --- Mock vue-i18n ---
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import useDocuments from '@/composables/useDocuments'

describe('UseDocuments', () => {
  let mockRefreshData: (patientId: number | null) => void

  beforeEach(() => {
    vi.clearAllMocks()
    mockRefreshData = vi.fn() as unknown as (patientId: number | null) => void
  })

  // --- Requirement 7.1: visible is false on initialization ---
  describe('initialization', () => {
    it('should have visible set to false initially', () => {
      const { visible } = useDocuments(mockRefreshData)
      expect(visible.value).toBe(false)
    })
  })

  // --- Requirement 7.2: toggleVisible toggles visible between true and false ---
  describe('toggleVisible', () => {
    it('should toggle visible from false to true', () => {
      const { visible, toggleVisible } = useDocuments(mockRefreshData)
      expect(visible.value).toBe(false)

      toggleVisible()
      expect(visible.value).toBe(true)
    })

    it('should toggle visible from true back to false', () => {
      const { visible, toggleVisible } = useDocuments(mockRefreshData)

      toggleVisible()
      expect(visible.value).toBe(true)

      toggleVisible()
      expect(visible.value).toBe(false)
    })
  })

  // --- Requirement 7.3: handleUploadSuccess shows success toast and calls refreshData ---
  describe('handleUploadSuccess', () => {
    it('should display a success toast with the translated message', () => {
      const { handleUploadSuccess } = useDocuments(mockRefreshData)

      handleUploadSuccess('document_uploaded', 42)

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'success',
          summary: 'Téléversement',
          detail: 'api.document_uploaded'
        })
      )
    })

    it('should call refreshData with the patientId', () => {
      const { handleUploadSuccess } = useDocuments(mockRefreshData)

      handleUploadSuccess('document_uploaded', 42)

      expect(mockRefreshData).toHaveBeenCalledWith(42)
    })
  })
})

// Feature: frontend-test-coverage, Property 11: Idempotence du double toggle de visibilité
import fc from 'fast-check'

describe('UseDocuments — Property-Based Tests', () => {
  // **Validates: Requirements 7.2**
  it('Property 11: double toggle returns visible to its initial value', () => {
    fc.assert(
      fc.property(fc.boolean(), (initialVisible) => {
        const mockRefresh = vi.fn()
        const { visible, toggleVisible } = useDocuments(mockRefresh)

        // Set the initial state
        visible.value = initialVisible

        // Toggle twice
        toggleVisible()
        toggleVisible()

        // Must return to initial value
        expect(visible.value).toBe(initialVisible)
      }),
      { numRuns: 100 }
    )
  })
})
