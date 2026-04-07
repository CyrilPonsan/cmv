import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// --- Mock vue-router ---
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ params: { id: '1' } })
}))

// --- Mock user store ---
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    role: 'home',
    getUserInfos: vi.fn(),
    logout: vi.fn(),
    signout: vi.fn()
  })
}))

// --- Mock useHttp ---
const mockSendRequest = vi.fn()
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: ref(null),
    axiosInstance: {}
  })
}))

// --- Mock PrimeVue useToast ---
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: mockToastAdd })
}))

// --- Mock vue-i18n ---
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import useDocumentManagement from '@/composables/useDocumentManagement'

describe('UseDocumentManagement', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
  })

  // --- Requirement 8.1: visible is false and documentToDelete is null on initialization ---
  describe('initialization', () => {
    it('should have visible set to false initially', () => {
      const { visible } = useDocumentManagement()
      expect(visible.value).toBe(false)
    })

    it('should have documentToDelete set to null initially', () => {
      const { documentToDelete } = useDocumentManagement()
      expect(documentToDelete.value).toBeNull()
    })
  })

  // --- Requirement 8.2: deleteDocument sends DELETE to /patients/delete/documents/delete/{id} ---
  describe('deleteDocument', () => {
    it('should send a DELETE request to /patients/delete/documents/delete/{id}', () => {
      const { deleteDocument } = useDocumentManagement()
      const onSuccess = vi.fn()

      deleteDocument(42, onSuccess)

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients/delete/documents/delete/42', method: 'delete' },
        expect.any(Function)
      )
    })
  })

  // --- Requirement 8.3: Success toast, onSuccess callback, and documentToDelete reset ---
  describe('deleteDocument success', () => {
    it('should display a success toast when deletion succeeds', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_deleted' })
      })

      const { deleteDocument } = useDocumentManagement()
      const onSuccess = vi.fn()

      deleteDocument(10, onSuccess)

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'success',
          summary: 'components.documentsList.deletion',
          detail: 'api.document_deleted'
        })
      )
    })

    it('should execute the onSuccess callback when deletion succeeds', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_deleted' })
      })

      const { deleteDocument } = useDocumentManagement()
      const onSuccess = vi.fn()

      deleteDocument(10, onSuccess)

      expect(onSuccess).toHaveBeenCalled()
    })

    it('should reset documentToDelete to null when deletion succeeds', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_deleted' })
      })

      const { deleteDocument, documentToDelete } = useDocumentManagement()
      documentToDelete.value = { id_document: 10, document_type: 'ordonnance', filename: 'test.pdf', created_at: '2024-01-01' } as any

      deleteDocument(10, vi.fn())

      expect(documentToDelete.value).toBeNull()
    })
  })
})


// Feature: frontend-test-coverage, Property 12: Construction de l'URL de suppression de document
import fc from 'fast-check'

describe('UseDocumentManagement - Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
  })

  // **Validates: Requirements 8.2**
  it('Property 12: for any positive integer document ID, deleteDocument must trigger a DELETE to /patients/delete/documents/delete/{id}', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1_000_000 }),
        (docId) => {
          mockSendRequest.mockReset()

          const { deleteDocument } = useDocumentManagement()
          const onSuccess = vi.fn()

          deleteDocument(docId, onSuccess)

          expect(mockSendRequest).toHaveBeenCalledWith(
            { path: `/patients/delete/documents/delete/${docId}`, method: 'delete' },
            expect.any(Function)
          )
        }
      ),
      { numRuns: 100 }
    )
  })
})
