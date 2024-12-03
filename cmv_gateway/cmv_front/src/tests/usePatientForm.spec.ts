import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import usePatientForm from '@/composables/usePatientForm'
import { nextTick, ref, effectScope } from 'vue'

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
      const form = usePatientForm()

      expect(form.civilites.value).toEqual(['Monsieur', 'Madame', 'Autre', 'Roberto'])
      expect(form.civilite.value).toBe('Autre')
      expect(form.date_de_naissance.value).toBeInstanceOf(Date)
      expect(form.isLoading.value).toBe(false)
    })
  })

  it('met à jour la civilité correctement', () => {
    scope.run(() => {
      const form = usePatientForm()
      form.updateCivilite('Monsieur')
      expect(form.civilite.value).toBe('Monsieur')
    })
  })

  it('met à jour la date de naissance correctement', () => {
    const form = usePatientForm()
    const newDate = new Date('2000-01-01')
    form.updateDateDeNaissance(newDate)
    expect(form.date_de_naissance.value).toBe(newDate)
  })

  it('soumet les données correctement et gère la réponse succès', async () => {
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

    mockSendRequest.mockImplementationOnce((config, callback) => {
      callback(mockResponse)
    })

    form.onSubmit(testData)
    await nextTick()

    // Vérifie que la requête a été envoyée avec les bonnes données
    expect(mockSendRequest).toHaveBeenCalledWith(
      {
        path: '/patients/patients',
        method: 'POST',
        data: {
          ...testData,
          civilite: form.civilite.value,
          date_de_naissance: form.date_de_naissance.value
        }
      },
      expect.any(Function)
    )

    // Vérifie que le toast de succès a été affiché
    expect(toastMock.add).toHaveBeenCalledWith({
      summary: 'Patient ajouté',
      detail: mockResponse.message,
      severity: 'success',
      closable: true,
      life: 5000
    })
  })
})
