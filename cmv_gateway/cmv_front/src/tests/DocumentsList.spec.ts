import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentsList from '@/components/documents/DocumentsList.vue'
import type Document from '@/models/document'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'

const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: {
    fr
  }
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

// Mock de useHttp
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    isLoading: false,
    sendRequest: vi.fn()
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
    expect(message.text()).toBe('-')
  })
})
