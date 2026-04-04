import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { ref } from 'vue'

// ---- Mock composables ----

const mockFetchPatientData = vi.fn()
vi.mock('@/composables/usePatient', () => ({
  default: () => ({
    detailPatient: ref({
      id_patient: 1,
      nom: 'Dupont',
      prenom: 'Jean',
      documents: [],
      latest_admission: null
    }),
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

vi.mock('@/composables/useDocuments', () => ({
  default: () => ({
    visible: ref(false),
    toggleVisible: vi.fn(),
    handleUploadSuccess: vi.fn()
  })
}))

vi.mock('@/composables/usePatientForm', () => ({
  default: () => ({
    civilites: ref(['Monsieur', 'Madame', 'Autre']),
    isEditing: ref(false),
    isLoading: ref(false),
    onCreatePatient: vi.fn(),
    onUpdatePatient: vi.fn(),
    schema: {}
  })
}))

const mockSendRequest = vi.fn()
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: ref(null),
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
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: vi.fn() })
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
  useToast: () => ({ add: vi.fn() })
}))

vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    props: ['label', 'icon', 'severity', 'loading', 'disabled', 'fluid', 'text', 'rounded', 'variant', 'outlined'],
    template: '<button data-testid="button">{{ label }}</button>'
  }
}))

// ---- Mock vee-validate ----
vi.mock('vee-validate', () => ({
  useForm: () => ({
    handleSubmit: (fn: Function) => (e: Event) => { e?.preventDefault?.(); fn({}) },
    setFieldValue: vi.fn()
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
  })
})
