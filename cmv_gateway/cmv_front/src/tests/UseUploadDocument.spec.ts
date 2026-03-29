import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, nextTick } from 'vue'
import fc from 'fast-check'

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
const mockHttpError = ref<string | null>(null)
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: mockHttpError,
    axiosInstance: {}
  })
}))

// --- Mock PrimeVue (useToast is imported from 'primevue') ---
const mockToastAdd = vi.fn()
vi.mock('primevue', () => ({
  useToast: () => ({ add: mockToastAdd })
}))

// --- Mock vue-i18n ---
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import useUploadDocument from '@/composables/useUploadDocument'

describe('UseUploadDocument', () => {
  const patientId = 42
  let mockEmit: any

  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
    mockHttpError.value = null
    mockEmit = vi.fn()
  })

  // --- Requirement 9.1: documentTypes contains 8 types and isValid is false on initialization ---
  describe('initialization', () => {
    it('should have documentTypes with 8 document types', () => {
      const { documentTypes } = useUploadDocument(patientId, mockEmit)
      expect(documentTypes.value).toHaveLength(8)
    })

    it('should have isValid set to false initially', () => {
      const { isValid } = useUploadDocument(patientId, mockEmit)
      expect(isValid.value).toBe(false)
    })

    it('should have selectedFile set to null initially', () => {
      const { selectedFile } = useUploadDocument(patientId, mockEmit)
      expect(selectedFile.value).toBeNull()
    })

    it('should have selectedDocumentType set to null initially', () => {
      const { selectedDocumentType } = useUploadDocument(patientId, mockEmit)
      expect(selectedDocumentType.value).toBeNull()
    })
  })

  // --- Requirement 9.2: isValid becomes true when file and type are selected ---
  describe('isValid computed', () => {
    it('should be true when both file and document type are selected', () => {
      const { isValid, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      expect(isValid.value).toBe(true)
    })

    it('should be false when only file is selected', () => {
      const { isValid, selectedFile } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      expect(isValid.value).toBe(false)
    })

    it('should be false when only document type is selected', () => {
      const { isValid, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      expect(isValid.value).toBe(false)
    })
  })

  // --- Requirement 9.3: onSubmit sends POST multipart/form-data to /patients/upload/documents/create/{patientId} ---
  describe('onSubmit', () => {
    it('should send a POST request with FormData to the correct endpoint', () => {
      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(mockSendRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          path: `/patients/upload/documents/create/${patientId}`,
          method: 'POST',
          headers: { 'Content-Type': 'multipart/form-data' }
        }),
        expect.any(Function)
      )
    })

    it('should include document_type and file in the FormData', () => {
      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      const callArgs = mockSendRequest.mock.calls[0][0]
      const formData: FormData = callArgs.data
      expect(formData).toBeInstanceOf(FormData)
      expect(formData.get('document_type')).toBe('miscellaneous')
      expect(formData.get('file')).toBeInstanceOf(File)
    })

    it('should not send a request when file is null', () => {
      const { onSubmit, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(mockSendRequest).not.toHaveBeenCalled()
    })

    it('should not send a request when document type is null', () => {
      const { onSubmit, selectedFile } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      onSubmit()

      expect(mockSendRequest).not.toHaveBeenCalled()
    })
  })

  // --- Requirement 9.4: Events "refresh" and "update:visible" emitted after success, and reset ---
  describe('onSubmit success', () => {
    it('should emit "refresh" with message and patientId after successful upload', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_uploaded' })
      })

      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(mockEmit).toHaveBeenCalledWith('refresh', 'document_uploaded', patientId)
    })

    it('should emit "update:visible" with false after successful upload', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_uploaded' })
      })

      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(mockEmit).toHaveBeenCalledWith('update:visible', false)
    })

    it('should reset selectedFile to null after successful upload', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_uploaded' })
      })

      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(selectedFile.value).toBeNull()
    })

    it('should reset selectedDocumentType to null after successful upload', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'document_uploaded' })
      })

      const { onSubmit, selectedFile, selectedDocumentType } = useUploadDocument(patientId, mockEmit)

      selectedFile.value = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      selectedDocumentType.value = { label: 'Divers', value: 'miscellaneous' }

      onSubmit()

      expect(selectedDocumentType.value).toBeNull()
    })
  })

  // --- Requirement 9.5: Error toast on upload failure ---
  describe('upload error', () => {
    it('should display an error toast when the error ref is updated', async () => {
      useUploadDocument(patientId, mockEmit)

      mockHttpError.value = 'upload_failed'

      await nextTick()

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'error',
          summary: 'Erreur',
          detail: 'api.upload_failed'
        })
      )
    })
  })
})

// Feature: frontend-test-coverage, Property 13: Validité du formulaire d'upload
// **Validates: Requirements 9.2**
describe('Property-based: upload form validity', () => {
  it('isValid should be true when both file and document type are non-null', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        fc.string({ minLength: 1 }),
        fc.string({ minLength: 1 }),
        (fileName: string, fileContent: string, docTypeValue: string) => {
          const { isValid, selectedFile, selectedDocumentType } = useUploadDocument(42, vi.fn() as any)

          selectedFile.value = new File([fileContent], fileName)
          selectedDocumentType.value = { label: docTypeValue, value: docTypeValue }

          expect(isValid.value).toBe(true)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('isValid should be false when file is null (regardless of document type)', () => {
    fc.assert(
      fc.property(
        fc.option(
          fc.record({
            label: fc.string({ minLength: 1 }),
            value: fc.string({ minLength: 1 })
          }),
          { nil: null }
        ),
        (docType: { label: string; value: string } | null) => {
          const { isValid, selectedFile, selectedDocumentType } = useUploadDocument(42, vi.fn() as any)

          selectedFile.value = null
          selectedDocumentType.value = docType

          expect(isValid.value).toBe(false)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('isValid should be false when document type is null (regardless of file)', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        fc.string({ minLength: 1 }),
        (fileName: string, fileContent: string) => {
          const { isValid, selectedFile, selectedDocumentType } = useUploadDocument(42, vi.fn() as any)

          selectedFile.value = new File([fileContent], fileName)
          selectedDocumentType.value = null

          expect(isValid.value).toBe(false)
        }
      ),
      { numRuns: 100 }
    )
  })
})
