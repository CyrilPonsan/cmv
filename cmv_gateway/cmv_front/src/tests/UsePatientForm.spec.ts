import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// --- Mock vue-router ---
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
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

// --- Mock PrimeVue useToast ---
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: mockToastAdd })
}))

// --- Mock vue-i18n ---
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import usePatientForm from '@/composables/usePatientForm'

describe('UsePatientForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
    mockToastAdd.mockReset()
    mockPush.mockReset()
    mockHttpError.value = null
  })

  // --- Requirement 6.1: civilites contains expected values and isEditing is false ---
  describe('initialization', () => {
    it('should have civilites containing ["Monsieur", "Madame", "Autre"]', () => {
      const { civilites } = usePatientForm(null)
      expect(civilites.value).toEqual(['Monsieur', 'Madame', 'Autre'])
    })

    it('should have isEditing set to false', () => {
      const { isEditing } = usePatientForm(null)
      expect(isEditing.value).toBe(false)
    })
  })

  // --- Requirement 6.2: onCreatePatient sends POST with formatted date ---
  describe('onCreatePatient', () => {
    it('should send a POST request to /patients/patients with date hours set to 12', () => {
      const { onCreatePatient } = usePatientForm(null)

      const testDate = new Date(1990, 0, 15, 8, 30, 45) // Jan 15, 1990 at 08:30:45
      const body = {
        civilite: 'Monsieur',
        nom: 'Dupont',
        prenom: 'Jean',
        date_de_naissance: testDate,
        adresse: '1 rue de la Paix',
        code_postal: '75001',
        ville: 'Paris',
        telephone: '0601020304'
      }

      onCreatePatient(body)

      expect(mockSendRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          path: '/patients/patients',
          method: 'POST'
        }),
        expect.any(Function)
      )

      // Verify the date was formatted with hours set to 12:00:00
      const callData = mockSendRequest.mock.calls[0][0].data
      const sentDate = callData.date_de_naissance as Date
      expect(sentDate.getFullYear()).toBe(1990)
      expect(sentDate.getMonth()).toBe(0)
      expect(sentDate.getDate()).toBe(15)
      expect(sentDate.getHours()).toBe(12)
      expect(sentDate.getMinutes()).toBe(0)
      expect(sentDate.getSeconds()).toBe(0)
    })
  })

  // --- Requirement 6.3: Navigation to /patient/{id} after successful creation + success toast ---
  describe('onCreatePatient success', () => {
    it('should navigate to /patient/{id} and show success toast after creation', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'patient_created', id_patient: 42 })
      })

      const { onCreatePatient } = usePatientForm(null)

      onCreatePatient({
        civilite: 'Madame',
        nom: 'Martin',
        prenom: 'Marie',
        date_de_naissance: new Date(1985, 5, 20),
        adresse: '2 avenue des Champs',
        code_postal: '75008',
        ville: 'Paris',
        telephone: '0612345678'
      })

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'success',
          summary: 'Patient ajouté'
        })
      )
      expect(mockPush).toHaveBeenCalledWith('/patient/42')
    })
  })

  // --- Requirement 6.4: onUpdatePatient sends PUT and isEditing goes back to false ---
  describe('onUpdatePatient', () => {
    it('should send a PUT request to /patients/patients/{id} and set isEditing to false', () => {
      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ success: true, message: 'patient_updated', id_patient: 10 })
      })

      const { onUpdatePatient, isEditing } = usePatientForm(null)
      isEditing.value = true

      onUpdatePatient({
        id_patient: 10,
        civilite: 'Monsieur',
        nom: 'Dupont',
        prenom: 'Jean',
        date_de_naissance: '1990-01-15',
        adresse: '1 rue de la Paix',
        code_postal: '75001',
        ville: 'Paris',
        telephone: '0601020304'
      })

      expect(mockSendRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          path: '/patients/patients/10',
          method: 'PUT'
        }),
        expect.any(Function)
      )
      expect(isEditing.value).toBe(false)
    })
  })

  // --- Requirement 6.5: Error toast on submission failure ---
  describe('submission error', () => {
    it('should display an error toast when the error ref is updated', async () => {
      // Initialize the composable so the watcher is set up
      usePatientForm(null)

      // Simulate an error being set on the error ref
      mockHttpError.value = 'submission_failed'

      // Allow the watcher to trigger
      await new Promise((r) => setTimeout(r, 0))

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'error',
          summary: 'Erreur',
          detail: 'submission_failed'
        })
      )
    })
  })
})

// Feature: frontend-test-coverage, Property 10: Formatage de la date à midi lors de la création patient
import fc from 'fast-check'

describe('UsePatientForm - Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
    mockToastAdd.mockReset()
    mockPush.mockReset()
    mockHttpError.value = null
  })

  // **Validates: Requirements 6.2**
  it('Property 10: for any valid date of birth, onCreatePatient should set hours to 12, minutes to 0, seconds to 0 while preserving year, month, and day', () => {
    fc.assert(
      fc.property(
        fc.date({
          min: new Date(1900, 0, 1),
          max: new Date(2100, 11, 31)
        }),
        (randomDate) => {
          // Filter out invalid dates (e.g. Date(NaN)) that fast-check may generate
          fc.pre(!isNaN(randomDate.getTime()))

          mockSendRequest.mockReset()

          const { onCreatePatient } = usePatientForm(null)

          const body = {
            civilite: 'Monsieur',
            nom: 'Test',
            prenom: 'Patient',
            date_de_naissance: randomDate,
            adresse: '1 rue Test',
            code_postal: '75001',
            ville: 'Paris',
            telephone: '0600000000'
          }

          onCreatePatient(body)

          expect(mockSendRequest).toHaveBeenCalledTimes(1)

          const callData = mockSendRequest.mock.calls[0][0].data
          const sentDate = callData.date_de_naissance as Date

          // The date must preserve the original year, month, and day
          expect(sentDate.getFullYear()).toBe(randomDate.getFullYear())
          expect(sentDate.getMonth()).toBe(randomDate.getMonth())
          expect(sentDate.getDate()).toBe(randomDate.getDate())

          // Hours must be set to 12, minutes to 0, seconds to 0
          expect(sentDate.getHours()).toBe(12)
          expect(sentDate.getMinutes()).toBe(0)
          expect(sentDate.getSeconds()).toBe(0)
        }
      ),
      { numRuns: 100 }
    )
  })
})
