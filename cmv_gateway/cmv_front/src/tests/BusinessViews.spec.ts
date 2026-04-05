import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { ref } from 'vue'
import fc from 'fast-check'

// ---- Mock composables ----

const mockFetchPatientData = vi.fn()
const mockDetailPatient = ref<any>({
  id_patient: 1,
  nom: 'Dupont',
  prenom: 'Jean',
  documents: [],
  latest_admission: null
})
vi.mock('@/composables/usePatient', () => ({
  default: () => ({
    detailPatient: mockDetailPatient,
    fetchPatientData: mockFetchPatientData
  })
}))

vi.mock('@/composables/useChambresList', () => ({
  default: () => ({
    getChambres: vi.fn(),
    list: ref([]),
    isLoading: ref(false),
    error: ref(null),
    search: vi.fn(),
    searchValue: ref(''),
    searchBySelect: vi.fn(),
    suggestions: ref([]),
    resetSearchValue: vi.fn()
  })
}))

vi.mock('@/composables/useListPatients', () => ({
  default: () => ({
    dialogVisible: ref(false),
    selectedPatient: ref(null),
    showDeleteDialog: vi.fn(),
    onCancel: vi.fn(),
    onConfirm: vi.fn()
  })
}))

const mockVisible = ref(false)
const mockToggleVisible = vi.fn(() => {
  mockVisible.value = !mockVisible.value
})
vi.mock('@/composables/useDocuments', () => ({
  default: () => ({
    visible: mockVisible,
    toggleVisible: mockToggleVisible,
    handleUploadSuccess: vi.fn()
  })
}))

const mockIsEditing = ref(false)
vi.mock('@/composables/usePatientForm', () => ({
  default: () => ({
    civilites: ref(['Monsieur', 'Madame', 'Autre']),
    isEditing: mockIsEditing,
    isLoading: ref(false),
    onCreatePatient: vi.fn(),
    onUpdatePatient: vi.fn(),
    schema: {}
  })
}))

const mockSendRequest = vi.fn()
const mockError = ref<string | null>(null)
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: mockError,
    axiosInstance: {}
  })
}))

// ---- Mock stores ----
vi.mock('@/stores/services', () => ({
  useServices: () => ({
    servicesList: ref([]),
    servicesOptions: ref([]),
    fetchServices: vi.fn()
  })
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual('pinia')
  return {
    ...actual,
    storeToRefs: (store: Record<string, unknown>) => store
  }
})

// ---- Mock vue-i18n ----
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

// ---- Mock vue-router ----
const mockPush = vi.fn()
const mockBack = vi.fn()
const mockRoute = { params: { id: '42', patientId: '42' }, name: 'patient' }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush, back: mockBack }),
  useRoute: () => mockRoute
}))

// ---- Mock PrimeVue toast ----
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: mockToastAdd })
}))

// ---- Mock child components ----
vi.mock('@/components/PageHeader.vue', () => ({
  default: {
    name: 'PageHeader',
    props: ['title', 'description'],
    template: '<div data-testid="page-header">PageHeader</div>'
  }
}))

vi.mock('@/components/ListPatients.vue', () => ({
  default: {
    name: 'ListPatients',
    template: '<div data-testid="list-patients">ListPatients</div>'
  }
}))

vi.mock('@/components/PatientDetail.vue', () => ({
  default: {
    name: 'PatientDetail',
    props: ['detailPatient'],
    template: '<div data-testid="patient-detail">PatientDetail</div>'
  }
}))

vi.mock('@/components/documents/DocumentsList.vue', () => ({
  default: {
    name: 'DocumentsList',
    props: ['documents'],
    template: '<div data-testid="documents-list">DocumentsList</div>'
  }
}))

vi.mock('@/components/documents/DocumentUploadDialog.vue', () => ({
  default: {
    name: 'DocumentUpload',
    props: ['fullname', 'patientId', 'visible'],
    template: '<div data-testid="document-upload">DocumentUpload</div>'
  }
}))

vi.mock('@/components/create-update-patient/PatientForm.vue', () => ({
  default: {
    name: 'PatientForm',
    props: ['isLoading', 'onSubmit', 'schema', 'civilites', 'patientDetail'],
    template: '<div data-testid="patient-form">PatientForm</div>'
  }
}))

vi.mock('@/components/create-update-patient/PatientDataDisclaimer.vue', () => ({
  default: {
    name: 'PatientDataDisclaimer',
    template: '<div data-testid="patient-data-disclaimer">PatientDataDisclaimer</div>'
  }
}))

vi.mock('@/components/patient/PatientActions.vue', () => ({
  default: {
    name: 'PatientActions',
    emits: ['toggle-editing'],
    template: '<div data-testid="patient-actions">PatientActions</div>'
  }
}))

vi.mock('@/components/LatestAdmission.vue', () => ({
  default: {
    name: 'LatestAdmission',
    template: '<div data-testid="latest-admission">LatestAdmission</div>'
  }
}))

vi.mock('@/components/ServiceItem.vue', () => ({
  default: {
    name: 'ServiceItem',
    template: '<div data-testid="service-item">ServiceItem</div>'
  }
}))

// ---- Mock PrimeVue components ----
vi.mock('primevue', () => ({
  AutoComplete: {
    name: 'AutoComplete',
    props: ['modelValue', 'suggestions', 'dropdown', 'size'],
    template: '<input data-testid="autocomplete" />'
  },
  Button: {
    name: 'Button',
    props: ['label', 'icon', 'severity', 'loading', 'disabled', 'fluid', 'text', 'rounded', 'variant', 'outlined'],
    template: '<button data-testid="button">{{ label }}</button>'
  },
  Checkbox: {
    name: 'Checkbox',
    template: '<input type="checkbox" data-testid="checkbox" />'
  },
  DatePicker: {
    name: 'DatePicker',
    template: '<input data-testid="datepicker" />'
  },
  Message: {
    name: 'Message',
    template: '<div data-testid="message"><slot /></div>'
  },
  Select: {
    name: 'Select',
    props: ['options', 'modelValue', 'label', 'placeholder'],
    template: '<select data-testid="select"><option v-for="o in options" :key="o">{{ o }}</option></select>'
  },
  Slider: {
    name: 'Slider',
    template: '<input type="range" data-testid="slider" />'
  },
  InputNumber: {
    name: 'InputNumber',
    template: '<input type="number" data-testid="input-number" />'
  },
  useToast: () => ({ add: mockToastAdd })
}))

vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    props: ['label', 'icon', 'severity', 'loading', 'disabled', 'fluid', 'text', 'rounded', 'variant', 'outlined'],
    template: '<button data-testid="button">{{ label }}</button>'
  }
}))

// ---- Mock vee-validate ----
const mockSetFieldValue = vi.fn()
vi.mock('vee-validate', () => ({
  useForm: () => ({
    handleSubmit: (fn: Function) => (e: Event) => {
      e?.preventDefault?.();
      fn({
        ambulatoire: 'Ambulatoire',
        entree_le: new Date('2025-01-15'),
        sortie_prevue_le: new Date('2025-01-20'),
        services: 'Cardiologie'
      })
    },
    setFieldValue: mockSetFieldValue
  }),
  Field: {
    name: 'Field',
    props: ['name'],
    template: '<div data-testid="field"><slot :value="null" :handleChange="() => {}" :errorMessage="null" /></div>'
  }
}))

// ---- Mock stores ----
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    role: 'home',
    logout: vi.fn()
  })
}))

// ---- Import views ----
import AccueilView from '@/views/AccueilView.vue'
import PatientView from '@/views/PatientView.vue'
import AddPatientView from '@/views/AddPatientView.vue'
import ChambresView from '@/views/ChambresView.vue'
import AdmissionView from '@/views/AdmissionView.vue'

/**
 * Tests des vues métier : AccueilView, PatientView, AddPatientView, ChambresView, AdmissionView
 * Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5
 */
describe('BusinessViews', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockError.value = null
    mockDetailPatient.value = {
      id_patient: 1,
      nom: 'Dupont',
      prenom: 'Jean',
      documents: [],
      latest_admission: null
    }
    mockIsEditing.value = false
    mockVisible.value = false
  })

  /**
   * AccueilView — Validates: Requirement 12.1
   */
  describe('AccueilView', () => {
    it('should render PageHeader component', () => {
      const wrapper = shallowMount(AccueilView)
      const pageHeader = wrapper.findComponent({ name: 'PageHeader' })
      expect(pageHeader.exists()).toBe(true)
    })

    it('should render ListPatients component', () => {
      const wrapper = shallowMount(AccueilView)
      const listPatients = wrapper.findComponent({ name: 'ListPatients' })
      expect(listPatients.exists()).toBe(true)
    })
  })

  /**
   * PatientView — Validates: Requirement 12.2
   */
  describe('PatientView', () => {
    it('should call fetchPatientData with the route ID on mount', () => {
      shallowMount(PatientView)
      expect(mockFetchPatientData).toHaveBeenCalledWith(42)
    })

    it('should render PatientDetail component', () => {
      const wrapper = shallowMount(PatientView)
      const patientDetail = wrapper.findComponent({ name: 'PatientDetail' })
      expect(patientDetail.exists()).toBe(true)
    })

    it('should render DocumentsList component', () => {
      const wrapper = shallowMount(PatientView)
      const documentsList = wrapper.findComponent({ name: 'DocumentsList' })
      expect(documentsList.exists()).toBe(true)
    })

    /**
     * PatientView interactions — Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
     */
    it('should toggle to editing mode when PatientActions emits toggle-editing', async () => {
      const wrapper = shallowMount(PatientView)
      // Initially PatientDetail is shown, PatientForm is not
      expect(wrapper.findComponent({ name: 'PatientDetail' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'PatientForm' }).exists()).toBe(false)

      // Emit toggle-editing from PatientActions
      const patientActions = wrapper.findComponent({ name: 'PatientActions' })
      await patientActions.vm.$emit('toggle-editing', true)
      await wrapper.vm.$nextTick()

      // PatientForm should now be shown, PatientDetail hidden
      expect(wrapper.findComponent({ name: 'PatientForm' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'PatientDetail' }).exists()).toBe(false)
    })

    it('should return to read mode when clicking "Retour aux informations du patient"', async () => {
      // Start in editing mode
      mockIsEditing.value = true
      const wrapper = shallowMount(PatientView)

      // PatientForm should be shown
      expect(wrapper.findComponent({ name: 'PatientForm' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'PatientDetail' }).exists()).toBe(false)

      // Click the "Retour aux informations du patient" link
      const backLink = wrapper.find('.text-primary-500.underline.cursor-pointer')
      expect(backLink.exists()).toBe(true)
      await backLink.trigger('click')
      await wrapper.vm.$nextTick()

      // PatientDetail should be shown again
      expect(wrapper.findComponent({ name: 'PatientDetail' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'PatientForm' }).exists()).toBe(false)
    })

    it('should update DocumentUpload visible prop when toggleVisible is called', async () => {
      const wrapper = shallowMount(PatientView)
      const docUpload = wrapper.findComponent({ name: 'DocumentUpload' })
      expect(docUpload.exists()).toBe(true)
      expect(docUpload.props('visible')).toBe(false)

      // Call toggleVisible to flip the visible state
      mockToggleVisible()
      await wrapper.vm.$nextTick()

      const docUploadAfter = wrapper.findComponent({ name: 'DocumentUpload' })
      expect(docUploadAfter.props('visible')).toBe(true)
    })

    it('should not render PatientDetail, DocumentsList and DocumentUpload when detailPatient is null', async () => {
      mockDetailPatient.value = null
      const wrapper = shallowMount(PatientView)

      expect(wrapper.findComponent({ name: 'PatientDetail' }).exists()).toBe(false)
      expect(wrapper.findComponent({ name: 'DocumentsList' }).exists()).toBe(false)
      expect(wrapper.findComponent({ name: 'DocumentUpload' }).exists()).toBe(false)
    })
  })

  /**
   * AddPatientView — Validates: Requirement 12.3
   */
  describe('AddPatientView', () => {
    it('should render PatientForm component', () => {
      const wrapper = shallowMount(AddPatientView)
      const patientForm = wrapper.findComponent({ name: 'PatientForm' })
      expect(patientForm.exists()).toBe(true)
    })

    it('should render PatientDataDisclaimer component', () => {
      const wrapper = shallowMount(AddPatientView)
      const disclaimer = wrapper.findComponent({ name: 'PatientDataDisclaimer' })
      expect(disclaimer.exists()).toBe(true)
    })
  })

  /**
   * ChambresView — Validates: Requirement 12.4
   */
  describe('ChambresView', () => {
    it('should render PageHeader component', () => {
      const wrapper = shallowMount(ChambresView)
      const pageHeader = wrapper.findComponent({ name: 'PageHeader' })
      expect(pageHeader.exists()).toBe(true)
    })

    it('should render AutoComplete search bar', () => {
      const wrapper = shallowMount(ChambresView)
      const autoComplete = wrapper.findComponent({ name: 'AutoComplete' })
      expect(autoComplete.exists()).toBe(true)
    })
  })

  /**
   * AdmissionView — Validates: Requirement 12.5
   */
  describe('AdmissionView', () => {
    const mountAdmission = () =>
      shallowMount(AdmissionView, {
        global: {
          stubs: {
            Form: false,
            Field: false
          }
        }
      })

    it('should render the admission form with date d\'entrée field', () => {
      const wrapper = mountAdmission()
      const dateEntreeLabel = wrapper.find('label[for="entree_le"]')
      expect(dateEntreeLabel.exists()).toBe(true)
      expect(dateEntreeLabel.text()).toContain("Date d'entrée")
    })

    it('should render the admission form with date de sortie field', () => {
      const wrapper = mountAdmission()
      const dateSortieLabel = wrapper.find('label[for="sortie_prevue_le"]')
      expect(dateSortieLabel.exists()).toBe(true)
      expect(dateSortieLabel.text()).toContain('Sortie prévue le')
    })

    it('should render the ambulatoire field', () => {
      const wrapper = mountAdmission()
      const ambulatoireLabel = wrapper.find('label[for="ambulatoire"]')
      expect(ambulatoireLabel.exists()).toBe(true)
      expect(ambulatoireLabel.text()).toContain('Ambulatoire')
    })

    it('should render the services field', () => {
      const wrapper = mountAdmission()
      const servicesLabel = wrapper.find('label[for="services"]')
      expect(servicesLabel.exists()).toBe(true)
      expect(servicesLabel.text()).toContain('Services')
    })

    /**
     * AdmissionView interactions — Validates: Requirements 9.1, 9.2, 9.3, 9.5, 9.6
     */
    it('should call sendRequest with admission data when form is submitted', async () => {
      const wrapper = mountAdmission()
      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(mockSendRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          path: '/patients/admissions',
          method: 'POST',
          body: expect.objectContaining({
            patient_id: '42',
            ambulatoire: true,
            entree_le: expect.any(Date),
            sortie_prevue_le: expect.any(Date)
          })
        }),
        expect.any(Function)
      )
    })

    it('should show success toast and navigate to patient page after successful admission creation', async () => {
      mockSendRequest.mockImplementation((config: Record<string, unknown>, callback: Function) => {
        if (config.path === '/patients/admissions') {
          callback({ ambulatoire: true, nom_chambre: null })
        }
      })

      const wrapper = mountAdmission()
      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'success'
        })
      )
      expect(mockPush).toHaveBeenCalledWith('/patient/42')
    })

    it('should call sendRequest with prediction path when "Estimer la durée du séjour" is clicked', async () => {
      const wrapper = mountAdmission()
      // shallowMount stubs Button components — find by component name and label prop
      const buttons = wrapper.findAllComponents({ name: 'Button' })
      const predictButton = buttons.find((b) => b.props('label') === 'Estimer la durée du séjour')
      expect(predictButton).toBeDefined()
      await predictButton!.trigger('click')
      await wrapper.vm.$nextTick()

      expect(mockSendRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          path: '/ml/predictions/predict',
          method: 'POST'
        }),
        expect.any(Function)
      )
    })

    it('should show error toast when submission fails', async () => {
      const wrapper = mountAdmission()
      await wrapper.vm.$nextTick()

      mockError.value = 'Erreur lors de la création'
      await wrapper.vm.$nextTick()

      expect(mockToastAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'error',
          detail: 'Erreur lors de la création'
        })
      )
    })

    it('should call router.back() when "Annuler" button is clicked', async () => {
      const wrapper = mountAdmission()
      const buttons = wrapper.findAllComponents({ name: 'Button' })
      const cancelButton = buttons.find((b) => b.props('label') === 'Annuler')
      expect(cancelButton).toBeDefined()
      await cancelButton!.trigger('click')
      await wrapper.vm.$nextTick()

      expect(mockBack).toHaveBeenCalled()
    })

    // Feature: frontend-coverage-extension, Property 3: Arithmétique de date pour l'application de la prédiction
    /**
     * Property-based test: Date arithmetic for prediction application
     * Validates: Requirements 9.4
     *
     * For any number of predicted days (1-365), when the prediction is applied,
     * the exit date should equal entry date + predicted days, and ambulatoire
     * should switch to "Non ambulatoire".
     */
    it('should correctly compute exit date = entry date + predicted days for any prediction (PBT)', async () => {
      await fc.assert(
        fc.asyncProperty(fc.integer({ min: 1, max: 365 }), async (predictedDays) => {
          vi.clearAllMocks()

          // Mock sendRequest to simulate a prediction response with the generated days
          mockSendRequest.mockImplementation(
            (config: Record<string, unknown>, callback: Function) => {
              if (config.path === '/ml/predictions/predict') {
                callback({ prediction_id: 'test-id', predicted_length_of_stay: predictedDays })
              }
            }
          )

          const wrapper = mountAdmission()
          await wrapper.vm.$nextTick()

          // Step 1: Click "Estimer la durée du séjour" to trigger postPrediction
          const buttons = wrapper.findAllComponents({ name: 'Button' })
          const predictButton = buttons.find(
            (b) => b.props('label') === 'Estimer la durée du séjour'
          )
          expect(predictButton).toBeDefined()
          await predictButton!.trigger('click')
          await wrapper.vm.$nextTick()

          // Step 2: Click "Appliquer l'estimation" to trigger applyPrediction
          const updatedButtons = wrapper.findAllComponents({ name: 'Button' })
          const applyButton = updatedButtons.find(
            (b) => b.props('label') === "Appliquer l'estimation"
          )
          expect(applyButton).toBeDefined()
          await applyButton!.trigger('click')
          await wrapper.vm.$nextTick()

          // Step 3: Verify setFieldValue was called with the correct exit date
          // The entry date defaults to new Date() in the component
          // We verify the date arithmetic: sortie = entree + predictedDays * 86400000
          const sortieCall = mockSetFieldValue.mock.calls.find(
            (call: unknown[]) => call[0] === 'sortie_prevue_le'
          )
          expect(sortieCall).toBeDefined()
          const exitDate = sortieCall![1] as Date
          expect(exitDate).toBeInstanceOf(Date)

          // The entry date is new Date() at component creation time.
          // We verify the difference in days matches the prediction.
          const ambulatoireCall = mockSetFieldValue.mock.calls.find(
            (call: unknown[]) => call[0] === 'ambulatoire'
          )
          expect(ambulatoireCall).toBeDefined()
          expect(ambulatoireCall![1]).toBe('Non ambulatoire')

          // Verify date arithmetic: the difference between exit and entry should be predictedDays
          // We use the entry date from the component (entreeLe ref defaults to new Date())
          // Since we can't access the exact entreeLe ref, we verify via the setFieldValue calls
          // The component does: newSortie = new Date(entreeLe.value.getTime() + predictedDays * 24*60*60*1000)
          // We verify the exit date is approximately predictedDays from now
          const now = new Date()
          const diffMs = exitDate.getTime() - now.getTime()
          const diffDays = Math.round(diffMs / (24 * 60 * 60 * 1000))
          expect(diffDays).toBe(predictedDays)
        }),
        { numRuns: 100 }
      )
    })
  })
})
