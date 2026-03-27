import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// --- Mock vue-router ---
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ name: 'test' })
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

// --- Mock useLazyLoad ---
const mockGetData = vi.fn()
const mockLazyState = ref({ first: 0, rows: 10, sortField: 'nom', sortOrder: 1 })
const mockLoading = ref(false)
const mockSearch = ref('')
const mockResult = ref<any[]>([])
const mockTotalRecords = ref(0)
vi.mock('@/composables/useLazyLoad', () => ({
  default: () => ({
    getData: mockGetData,
    lazyState: mockLazyState,
    loading: mockLoading,
    onLazyLoad: vi.fn(),
    onResetFilter: vi.fn(),
    onSort: vi.fn(),
    result: mockResult,
    search: mockSearch,
    totalRecords: mockTotalRecords
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

// --- Mock lifecycle hooks (no-op in test) ---
vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onBeforeMount: vi.fn((cb: () => void) => cb()),
    onUnmounted: vi.fn()
  }
})

import useListPatients from '@/composables/useListPatients'
import type PatientsListItem from '@/models/patients-list-item'

const createMockPatient = (overrides: Partial<PatientsListItem> = {}): PatientsListItem => ({
  id_patient: 1,
  nom: 'Dupont',
  prenom: 'Jean',
  date_de_naissance: '1990-01-15',
  telephone: '0601020304',
  ...overrides
})

describe('UseListPatients', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockHttpError.value = null
    mockSendRequest.mockReset()
    mockGetData.mockReset()
    mockToastAdd.mockReset()
  })

  // --- Requirement 4.1: showDeleteDialog updates selectedPatient and dialogVisible ---
  describe('showDeleteDialog', () => {
    it('should set selectedPatient to the given patient', () => {
      const { showDeleteDialog, selectedPatient } = useListPatients()
      const patient = createMockPatient({ id_patient: 42, nom: 'Martin' })

      showDeleteDialog(patient)

      expect(selectedPatient.value).toEqual(patient)
    })

    it('should set dialogVisible to true', () => {
      const { showDeleteDialog, dialogVisible } = useListPatients()
      const patient = createMockPatient()

      showDeleteDialog(patient)

      expect(dialogVisible.value).toBe(true)
    })
  })

  // --- Requirement 4.2: onCancel resets selectedPatient and dialogVisible ---
  describe('onCancel', () => {
    it('should reset selectedPatient to null', () => {
      const { showDeleteDialog, onCancel, selectedPatient } = useListPatients()
      const patient = createMockPatient()

      showDeleteDialog(patient)
      expect(selectedPatient.value).not.toBeNull()

      onCancel()
      expect(selectedPatient.value).toBeNull()
    })

    it('should set dialogVisible to false', () => {
      const { showDeleteDialog, onCancel, dialogVisible } = useListPatients()
      const patient = createMockPatient()

      showDeleteDialog(patient)
      expect(dialogVisible.value).toBe(true)

      onCancel()
      expect(dialogVisible.value).toBe(false)
    })
  })

  // --- Requirement 4.3: onConfirm sends DELETE request and closes dialog ---
  describe('onConfirm', () => {
    it('should send a DELETE request with the selected patient ID', () => {
      const { showDeleteDialog, onConfirm } = useListPatients()
      const patient = createMockPatient({ id_patient: 99 })

      showDeleteDialog(patient)
      onConfirm()

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients/delete/patients/99', method: 'delete' },
        expect.any(Function)
      )
    })

    it('should close the dialog after confirming', () => {
      const { showDeleteDialog, onConfirm, dialogVisible } = useListPatients()
      const patient = createMockPatient()

      showDeleteDialog(patient)
      onConfirm()

      expect(dialogVisible.value).toBe(false)
    })

    it('should reset selectedPatient to null after confirming', () => {
      const { showDeleteDialog, onConfirm, selectedPatient } = useListPatients()
      const patient = createMockPatient()

      showDeleteDialog(patient)
      onConfirm()

      expect(selectedPatient.value).toBeNull()
    })
  })

  // --- Requirement 4.4: Success toast and getData recall after successful deletion ---
  describe('onTrash success', () => {
    it('should display a success toast when deletion succeeds', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        if (req.method === 'delete') {
          applyData({ success: true, message: 'patient_deleted' })
        }
      })

      const { onTrash } = useListPatients()
      onTrash(1)

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'success',
          summary: 'patients.home.toasters.delete.success.summary',
          detail: 'api.patient_deleted'
        })
      )
    })

    it('should call getData to refresh the list after successful deletion', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        if (req.method === 'delete') {
          applyData({ success: true, message: 'patient_deleted' })
        }
      })

      // Clear initial getData call from onBeforeMount
      mockGetData.mockClear()

      const { onTrash } = useListPatients()

      // Clear the onBeforeMount getData call
      mockGetData.mockClear()

      onTrash(5)

      expect(mockGetData).toHaveBeenCalled()
    })
  })

  // --- Requirement 4.5: Error toast on deletion failure ---
  describe('onTrash error', () => {
    it('should display an error toast when the error ref is updated', async () => {
      const { error } = useListPatients()

      // Simulate an error being set on the error ref (watched by the composable)
      mockHttpError.value = 'deletion_failed'

      // Allow the watcher to trigger
      await new Promise((r) => setTimeout(r, 0))

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'error',
          summary: 'patients.home.toasters.delete.error.summary',
          detail: 'api.deletion_failed'
        })
      )
    })
  })
})
