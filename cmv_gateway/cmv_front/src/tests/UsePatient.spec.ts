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

import usePatient from '@/composables/usePatient'

describe('UsePatient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
  })

  // --- Requirement 5.1: detailPatient is null on initialization ---
  describe('initialization', () => {
    it('should have detailPatient as null initially', () => {
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

    it('should update detailPatient when the request succeeds', () => {
      const mockPatient = {
        id_patient: 42,
        nom: 'Dupont',
        prenom: 'Jean',
        civilite: 'Monsieur',
        date_de_naissance: '1990-01-15',
        adresse: '1 rue de la Paix',
        code_postal: '75001',
        ville: 'Paris',
        telephone: '0601020304',
        documents: [],
        latest_admission: null
      }

      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData(mockPatient)
      })

      const { fetchPatientData, detailPatient } = usePatient()
      fetchPatientData(42)

      expect(detailPatient.value).toEqual(mockPatient)
    })
  })
})

// Feature: frontend-test-coverage, Property 9: Construction de l'URL fetchPatientData
import fc from 'fast-check'

describe('UsePatient - Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
  })

  // **Validates: Requirements 5.2**
  it('Property 9: fetchPatientData(id) must trigger a request to /patients/patients/detail/{id} for any positive integer', () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 1_000_000 }), (patientId) => {
        mockSendRequest.mockReset()
        const { fetchPatientData } = usePatient()

        fetchPatientData(patientId)

        expect(mockSendRequest).toHaveBeenCalledOnce()
        expect(mockSendRequest).toHaveBeenCalledWith(
          { path: `/patients/patients/detail/${patientId}` },
          expect.any(Function)
        )
      }),
      { numRuns: 100 }
    )
  })
})
