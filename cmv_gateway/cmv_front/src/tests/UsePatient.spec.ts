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
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: ref(null),
    axiosInstance: {}
  })
}))

import usePatient from '@/composables/usePatient'

describe('UsePatient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
  })

  // --- Requirement 5.1: detailPatient is null at initialization ---
  describe('initialization', () => {
    it('should have detailPatient as null at initialization', () => {
      const { detailPatient } = usePatient()
      expect(detailPatient.value).toBeNull()
    })
  })

  // --- Requirement 5.2: fetchPatientData sends GET to /patients/patients/detail/{id} ---
  describe('fetchPatientData', () => {
    it('should send a GET request to /patients/patients/detail/{id}', () => {
      const { fetchPatientData } = usePatient()

      fetchPatientData(42)

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients/patients/detail/42' },
        expect.any(Function)
      )
    })

    it('should update detailPatient when data is received', () => {
      const mockPatient = {
        id_patient: 7,
        nom: 'Dupont',
        prenom: 'Jean',
        civilite: 'Monsieur',
        date_de_naissance: '1990-01-15',
        adresse: '1 rue de Paris',
        code_postal: '75001',
        ville: 'Paris',
        telephone: '0601020304'
      }

      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData(mockPatient)
      })

      const { fetchPatientData, detailPatient } = usePatient()
      fetchPatientData(7)

      expect(detailPatient.value).toEqual(mockPatient)
    })

    it('should construct the correct URL with the given patient ID', () => {
      const { fetchPatientData } = usePatient()

      fetchPatientData(123)

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients/patients/detail/123' },
        expect.any(Function)
      )
    })
  })
})
