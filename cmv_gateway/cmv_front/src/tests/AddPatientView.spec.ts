import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AddPatientView from '@/views/AddPatientView.vue'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import PrimeVue from 'primevue/config'

// Mock du composable usePatientForm
const mockFormData = {
  civilites: ['Monsieur', 'Madame', 'Autre', 'Roberto'],
  onCreatePatient: vi.fn(),
  schema: {},
  isLoading: false
}

vi.mock('@/composables/usePatientForm', () => ({
  default: () => mockFormData
}))

// Configuration i18n
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr }
})

describe('AddPatientView', () => {
  const mountComponent = () => {
    return mount(AddPatientView, {
      global: {
        plugins: [i18n, [PrimeVue, { ripple: true, inputStyle: 'filled' }]],
        stubs: {
          PageHeader: {
            name: 'PageHeader',
            template: '<div><h1>{{ title }}</h1><p>{{ description }}</p></div>',
            props: {
              title: String,
              description: String
            }
          },
          PatientForm: {
            name: 'PatientForm',
            template: '<div />',
            props: ['civilites', 'isLoading', 'onSubmit', 'schema']
          },
          PatientDataDisclaimer: true
        }
      }
    })
  }

  it('rend correctement la vue', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('affiche le titre et la description corrects', () => {
    const wrapper = mountComponent()
    const pageHeader = wrapper.findComponent({ name: 'PageHeader' })

    expect(pageHeader.exists()).toBe(true)
    expect(pageHeader.props('title')).toBe(fr.patients.add.title)
    expect(pageHeader.props('description')).toBe(fr.patients.add.description)
  })

  it('passe les bonnes props au composant PatientForm', () => {
    const wrapper = mountComponent()
    const patientForm = wrapper.findComponent({ name: 'PatientForm' })

    expect(patientForm.exists()).toBe(true)
    expect(patientForm.props()).toEqual({
      civilites: mockFormData.civilites,
      isLoading: mockFormData.isLoading,
      onSubmit: expect.any(Function),
      schema: mockFormData.schema
    })
  })

  it('affiche le composant PatientDataDisclaimer', () => {
    const wrapper = mountComponent()
    const disclaimer = wrapper.findComponent({ name: 'PatientDataDisclaimer' })
    expect(disclaimer.exists()).toBe(true)
  })
})
