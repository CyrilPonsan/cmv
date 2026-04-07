import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import DocumentsList from '@/components/documents/DocumentsList.vue'
import type Document from '@/models/document'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import en from '@/locales/en.json'

const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr, en }
})

vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button type="button" @click="$emit(\'click\')"><slot /></button>',
    props: ['label', 'icon', 'outlined']
  }
}))

vi.mock('primevue/dialog', () => ({
  default: {
    name: 'Dialog',
    template: '<div class="p-dialog"><slot /></div>'
  }
}))

// Mock du toast
const toastMock = {
  add: vi.fn()
}

vi.mock('primevue/usetoast', () => ({
  useToast: () => toastMock
}))

// Mock de useHttp — sendRequest accessible pour les assertions
const mockSendRequest = vi.fn()

vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    isLoading: ref(false),
    sendRequest: mockSendRequest
  })
}))

// Données de test
const mockDocuments: Document[] = [
  {
    id_document: 1,
    nom_fichier: 'Document.pdf',
    type_document: 'authorization_for_care',
    created_at: '2021-09-01T00:00:00.000Z'
  },
  {
    id_document: 2,
    nom_fichier: 'Document2.pdf',
    type_document: 'authorization_for_care',
    created_at: '2021-09-01T00:00:00.000Z'
  }
]

describe('DocumentsList', () => {
  let wrapper: any

  beforeEach(() => {
    mockSendRequest.mockReset()
    toastMock.add.mockReset()

    wrapper = mount(DocumentsList, {
      props: {
        documents: mockDocuments
      },
      global: {
        plugins: [i18n],
        stubs: {
          Dialog: true,
          DocumentPatient: true
        }
      }
    })
  })

  it('affiche correctement le titre de la liste', () => {
    const title = wrapper.find('h2')
    expect(title.text()).toBe(fr.components.documentsList.uploaded_documents)
  })

  it('affiche la liste des documents', () => {
    const documentItems = wrapper.findAllComponents({ name: 'DocumentPatient' })
    expect(documentItems).toHaveLength(mockDocuments.length)
  })

  it("émet l'événement toggle-visible lors du clic sur le bouton d'ajout", async () => {
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.exists()).toBe(true)
    await button.trigger('click')
    expect(wrapper.emitted('toggle-visible')).toBeTruthy()
  })

  it("émet l'événement download-document lors du téléchargement", async () => {
    const documentItem = wrapper.findComponent({ name: 'DocumentPatient' })
    await documentItem.vm.$emit('download-document', 1)
    expect(wrapper.emitted('download-document')).toBeTruthy()
    expect(wrapper.emitted('download-document')[0]).toEqual([1])
  })

  it('affiche le message "aucun document" quand la liste est vide', async () => {
    const emptyWrapper = mount(DocumentsList, {
      props: {
        documents: []
      },
      global: {
        plugins: [i18n],
        stubs: {
          Dialog: true,
          DocumentPatient: true
        }
      }
    })

    const message = emptyWrapper.find('p')
    expect(message.text()).toBe(fr.components.documentsList.no_document)
  })
})

/**
 * Tests du cycle de suppression de document
 * Exigences : 5.1, 5.2, 5.3
 */
describe('DocumentsList — cycle de suppression', () => {
  let wrapper: any

  // Stubs fonctionnels pour tester les interactions du cycle de suppression
  const DeleteConfirmationDialogStub = {
    name: 'DeleteConfirmationDialog',
    template: '<div class="delete-dialog" v-if="visible"><slot /></div>',
    props: ['visible', 'document', 'loading'],
    emits: ['confirm', 'cancel']
  }

  const DocumentPatientStub = {
    name: 'DocumentPatient',
    template: '<div class="document-patient"><slot /></div>',
    props: ['document', 'documentIndex'],
    emits: ['delete-document', 'download-document']
  }

  beforeEach(() => {
    mockSendRequest.mockReset()
    toastMock.add.mockReset()

    wrapper = mount(DocumentsList, {
      props: {
        documents: mockDocuments
      },
      global: {
        plugins: [i18n],
        stubs: {
          DeleteConfirmationDialog: DeleteConfirmationDialogStub,
          DocumentPatient: DocumentPatientStub,
          Dialog: true
        }
      }
    })
  })

  it('met à jour documentToDelete et rend visible le DeleteConfirmationDialog lors du clic sur suppression', async () => {
    // Le DeleteConfirmationDialog doit être initialement invisible (visible=false)
    const dialogBefore = wrapper.findComponent({ name: 'DeleteConfirmationDialog' })
    expect(dialogBefore.props('visible')).toBe(false)
    expect(dialogBefore.props('document')).toBeNull()

    // Émettre delete-document depuis le premier DocumentPatient
    const documentPatient = wrapper.findComponent({ name: 'DocumentPatient' })
    await documentPatient.vm.$emit('delete-document', mockDocuments[0].id_document)
    await nextTick()

    // Le dialogue doit maintenant être visible avec le document sélectionné
    const dialogAfter = wrapper.findComponent({ name: 'DeleteConfirmationDialog' })
    expect(dialogAfter.props('visible')).toBe(true)
    expect(dialogAfter.props('document')).toEqual(mockDocuments[0])
  })

  it('appelle deleteDocument avec l\'identifiant du document lors de la confirmation', async () => {
    // D'abord, déclencher la sélection du document pour suppression
    const documentPatient = wrapper.findComponent({ name: 'DocumentPatient' })
    await documentPatient.vm.$emit('delete-document', mockDocuments[0].id_document)
    await nextTick()

    // Confirmer la suppression
    const dialog = wrapper.findComponent({ name: 'DeleteConfirmationDialog' })
    await dialog.vm.$emit('confirm')
    await nextTick()

    // sendRequest doit être appelé avec le path contenant l'id du document et la méthode delete
    expect(mockSendRequest).toHaveBeenCalledWith(
      expect.objectContaining({
        path: `/patients/delete/documents/delete/${mockDocuments[0].id_document}`,
        method: 'delete'
      }),
      expect.any(Function)
    )
  })

  it('réinitialise documentToDelete à null et visible à false lors de l\'annulation', async () => {
    // D'abord, déclencher la sélection du document pour suppression
    const documentPatient = wrapper.findComponent({ name: 'DocumentPatient' })
    await documentPatient.vm.$emit('delete-document', mockDocuments[0].id_document)
    await nextTick()

    // Vérifier que le dialogue est visible
    let dialog = wrapper.findComponent({ name: 'DeleteConfirmationDialog' })
    expect(dialog.props('visible')).toBe(true)
    expect(dialog.props('document')).toEqual(mockDocuments[0])

    // Annuler la suppression
    await dialog.vm.$emit('cancel')
    await nextTick()

    // Le dialogue doit être fermé et le document réinitialisé
    dialog = wrapper.findComponent({ name: 'DeleteConfirmationDialog' })
    expect(dialog.props('visible')).toBe(false)
    expect(dialog.props('document')).toBeNull()
  })
})
