import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentUploadDialog from '@/components/documents/DocumentUploadDialog.vue'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import { ref } from 'vue'

// Configuration de vue-i18n pour les tests
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr }
})

// Mock des composants PrimeVue
// Mock du composant Button avec émission d'événement click
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button type="button" @click="$emit(\'click\')"><slot /></button>'
  }
}))

// Mock du composant Dialog avec gestion de la visibilité
vi.mock('primevue/dialog', () => ({
  default: {
    name: 'Dialog',
    template: '<div class="p-dialog" :class="{ \'p-dialog-visible\': visible }"><slot /></div>',
    props: ['visible']
  }
}))

// Mock du composant FileUpload avec émission d'événement select
vi.mock('primevue/fileupload', () => ({
  default: {
    name: 'FileUpload',
    template: '<div class="p-fileupload"><slot /></div>',
    emits: ['select']
  }
}))

// Mock du composant Select avec binding bidirectionnel
vi.mock('primevue/select', () => ({
  default: {
    name: 'Select',
    template:
      '<select v-model="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"></select>',
    props: ['modelValue', 'options']
  }
}))

// Mock du composable useUploadDocument avec les données de test
const emitMock = vi.fn()

const mockUseUploadDocument = {
  documentTypes: ref([
    {
      label: 'components.documentsList.document_types.health_insurance_card_certificate',
      value: 'health_insurance_card_certificate'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_care',
      value: 'authorization_for_care'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_treatment',
      value: 'authorization_for_treatment'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_visit',
      value: 'authorization_for_visit'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_overnight_stay',
      value: 'authorization_for_overnight_stay'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_departure',
      value: 'authorization_for_departure'
    },
    {
      label: 'components.documentsList.document_types.authorization_for_disconnection',
      value: 'authorization_for_disconnection'
    },
    { label: 'components.documentsList.document_types.miscellaneous', value: 'miscellaneous' }
  ]),
  isLoading: ref(false),
  isValid: ref(false),
  onSubmit: vi.fn().mockImplementation(() => {
    emitMock('update:visible', false)
    emitMock('refresh', 'document_created')
    return Promise.resolve()
  }),
  onSelect: vi.fn(),
  selectedDocumentType: ref(null),
  selectedFile: ref(null)
}

// Mock du composable useUploadDocument
vi.mock('@/composables/useUploadDocument', () => ({
  default: (patientId: number, emit: typeof emitMock) => {
    return {
      ...mockUseUploadDocument,
      onSubmit: () => mockUseUploadDocument.onSubmit(emit)
    }
  }
}))

describe('DocumentUploadDialog', () => {
  let wrapper: any

  // Fonction utilitaire pour monter le composant avec les props par défaut
  const mountComponent = (isValid = false) => {
    mockUseUploadDocument.isValid.value = isValid
    return mount(DocumentUploadDialog, {
      props: {
        fullname: 'John Doe',
        patientId: 1,
        visible: true
      },
      global: {
        plugins: [i18n]
      }
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseUploadDocument.isValid.value = true
    wrapper = mountComponent(true)
  })

  // Test du rendu initial du composant
  it('rend correctement le composant', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.p-dialog').exists()).toBe(true)
  })

  // Test de l'affichage du nom du patient
  it('affiche le nom du patient', () => {
    const patientName = wrapper.find('.capitalize')
    expect(patientName.text()).toBe('John Doe')
  })

  // Test de l'affichage de la liste des types de documents
  it('affiche la liste des types de documents', () => {
    const select = wrapper.findComponent({ name: 'Select' })
    expect(select.exists()).toBe(true)
    expect(select.props('options')).toEqual(mockUseUploadDocument.documentTypes.value)
  })

  // Test de la gestion de la sélection de fichier
  it('gère correctement la sélection de fichier', async () => {
    const fileUpload = wrapper.findComponent({ name: 'FileUpload' })
    const mockFile = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    await fileUpload.vm.$emit('select', { files: [mockFile] })

    expect(mockUseUploadDocument.onSelect).toHaveBeenCalled()
  })

  // Test de la fermeture de la modal
  it("émet l'événement update:visible lors de la fermeture", async () => {
    const cancelButton = wrapper.findAll('button').at(1)
    await cancelButton.trigger('click')

    expect(wrapper.emitted('update:visible')).toBeTruthy()
    expect(wrapper.emitted('update:visible')[0]).toEqual([false])
  })

  // Test de la soumission du formulaire
  it('gère correctement la soumission du formulaire', async () => {
    const form = wrapper.find('form')
    await form.trigger('submit')

    // Attendre que les promesses soient résolues
    await wrapper.vm.$nextTick()

    // Vérifier que onSubmit a été appelé
    expect(mockUseUploadDocument.onSubmit).toHaveBeenCalled()

    // Vérifier que les événements ont été émis
    expect(emitMock).toHaveBeenCalledWith('update:visible', false)
    expect(emitMock).toHaveBeenCalledWith('refresh', 'document_created')
  })

  // Test de la désactivation du bouton de soumission
  it('désactive le bouton de soumission quand le formulaire est invalide', async () => {
    const newWrapper = mountComponent(false)

    const buttons = newWrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
    const submitButton = buttons[0]
    expect(submitButton).toBeDefined()
    expect(submitButton.element.disabled).toBe(true)
  })
})
