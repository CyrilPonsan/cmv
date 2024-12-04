import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import usePatientForm from '@/composables/usePatientForm'
import { nextTick, ref, effectScope, type Ref } from 'vue'

// Mock du router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock du toast
const toastMock = {
  add: vi.fn()
}
vi.mock('primevue/usetoast', () => ({
  useToast: () => toastMock
}))

// Mock de useHttp
const mockSendRequest = vi.fn()
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    error: ref(''),
    isLoading: ref(false),
    sendRequest: mockSendRequest
  })
}))

// En haut du fichier
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

// Mise à jour de l'interface pour correspondre à l'implémentation
interface PatientForm {
  civilites: Ref<string[]>
  selectedCivilite: Ref<string>
  dateDeNaissance: Ref<Date>
  isLoading: Ref<boolean>
  schema: any
  updateSelectedCivilite: (civilite: string) => void
  updateDateDeNaissance: (date: Date) => void
  onSubmit: (data: Record<string, unknown>) => void
}

describe('usePatientForm', () => {
  let scope: any

  beforeEach(() => {
    vi.clearAllMocks()
    scope = effectScope()
  })

  afterEach(() => {
    scope.stop()
  })

  it('initialise avec les valeurs par défaut correctes', () => {
    scope.run(() => {
      const form = usePatientForm() as PatientForm
      expect(form.civilites.value).toEqual(['Monsieur', 'Madame', 'Autre', 'Roberto'])
      expect(form.selectedCivilite.value).toBe('Autre')
      expect(form.dateDeNaissance.value).toBeInstanceOf(Date)
      expect(form.isLoading.value).toBe(false)
    })
  })

  it('met à jour la civilité correctement', () => {
    scope.run(() => {
      const form = usePatientForm() as PatientForm
      form.updateSelectedCivilite('Monsieur')
      expect(form.selectedCivilite.value).toBe('Monsieur')
    })
  })

  it('met à jour la date de naissance correctement', () => {
    scope.run(() => {
      const form = usePatientForm() as PatientForm
      const newDate = new Date('2000-01-01')
      form.updateDateDeNaissance(newDate)
      expect(form.dateDeNaissance.value).toBe(newDate)
    })
  })

  it('soumet les données correctement et gère la réponse succès', async () => {
    scope.run(async () => {
      const form = usePatientForm()
      const testData = {
        nom: 'Dupont',
        prenom: 'Jean',
        adresse: '1 rue Test',
        code_postal: '75000',
        ville: 'Paris',
        telephone: '0123456789',
        email: 'test@test.com'
      }

      const mockResponse = {
        success: true,
        message: 'Patient créé',
        id_patient: 123
      }

      mockSendRequest.mockImplementationOnce((config: any, callback: any) => {
        callback(mockResponse)
      })

      form.onSubmit(testData)
      await nextTick()

      expect(mockSendRequest).toHaveBeenCalledWith(
        {
          path: '/patients/patients',
          method: 'POST',
          data: {
            ...testData
          }
        },
        expect.any(Function)
      )

      expect(toastMock.add).toHaveBeenCalledWith({
        summary: 'Patient ajouté',
        detail: mockResponse.message,
        severity: 'success',
        closable: true,
        life: 5000
      })
    })
  })
})
