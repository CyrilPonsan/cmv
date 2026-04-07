import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentPatient from '@/components/documents/DocumentPatient.vue'
import { createI18n } from 'vue-i18n'
import fc from 'fast-check'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

// Configuration i18n
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr, en },
  datetimeFormats: {
    fr: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    },
    en: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    }
  }
})

// Stubs PrimeVue
const stubs = {
  Card: {
    template:
      '<div class="card"><slot name="title"/><slot name="subtitle"/><slot name="content"/><slot name="footer"/></div>'
  },
  Button: {
    template:
      '<button @click="$emit(\'click\')" :disabled="disabled" :loading="loading"><slot />{{ label }}</button>',
    props: [
      'label',
      'severity',
      'loading',
      'disabled',
      'fluid',
      'icon',
      'text',
      'rounded',
      'variant',
      'outlined',
      'size'
    ]
  }
}

const createMockDocument = (overrides = {}) => ({
  id_document: 1,
  nom_fichier: 'test.pdf',
  type_document: 'authorization_for_care',
  created_at: '2024-01-15T10:00:00.000Z',
  ...overrides
})

describe('DocumentPatient', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(DocumentPatient, {
      props: {
        document: createMockDocument(),
        documentIndex: 0
      },
      global: {
        plugins: [i18n],
        stubs
      }
    })
  })

  it('affiche le numéro du document (index + 1), la date de création et le type de document', () => {
    const text = wrapper.text()
    // Document number = documentIndex + 1 = 1
    expect(text).toContain('Document')
    expect(text).toContain('1')
    // Date formatted by i18n 'short' format for fr locale: 15/01/2024
    expect(text).toContain('15/01/2024')
    // Type de document traduit
    expect(text).toContain('Autorisation de soins')
  })

  it('appelle window.open avec l\'URL correcte lors du clic sur téléchargement', async () => {
    const openSpy = vi.fn()
    vi.stubGlobal('open', openSpy)

    const buttons = wrapper.findAll('button')
    const downloadButton = buttons.find((b: any) => b.text().includes('Télécharger'))
    expect(downloadButton).toBeTruthy()

    openSpy.mockClear()
    await downloadButton!.trigger('click')

    expect(openSpy).toHaveBeenCalled()
    const matchingCall = openSpy.mock.calls.find(
      (call: any[]) => typeof call[0] === 'string' && call[0].includes('/patients/download/documents/download/1')
    )
    expect(matchingCall).toBeTruthy()
    expect(matchingCall![1]).toBe('_blank')

    vi.unstubAllGlobals()
  })

  it('émet "delete-document" avec l\'identifiant du document lors du clic sur suppression', async () => {
    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((b: any) => b.text().includes('Supprimer'))
    expect(deleteButton).toBeTruthy()
    await deleteButton!.trigger('click')

    expect(wrapper.emitted('delete-document')).toBeTruthy()
    expect(wrapper.emitted('delete-document')![0]).toEqual([1])
  })

  // Feature: frontend-coverage-extension, Property 1: URL de téléchargement contient l'identifiant du document
  // **Validates: Requirements 3.2**
  it('should call window.open with URL containing document ID for any ID (property-based)', async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 100000 }), async (docId) => {
        const openSpy = vi.fn()
        const originalOpen = window.open
        window.open = openSpy

        const w = mount(DocumentPatient, {
          props: {
            document: createMockDocument({ id_document: docId }),
            documentIndex: 0
          },
          global: {
            plugins: [i18n],
            stubs
          }
        })

        const buttons = w.findAll('button')
        const downloadButton = buttons.find((b: any) => b.text().includes('Télécharger'))
        await downloadButton!.trigger('click')

        const lastCall = openSpy.mock.calls[openSpy.mock.calls.length - 1]
        const url = lastCall?.[0] as string
        const containsId = url?.includes(`/patients/download/documents/download/${docId}`)
        const isBlank = lastCall?.[1] === '_blank'

        w.unmount()
        window.open = originalOpen

        return containsId && isBlank
      }),
      { numRuns: 100 }
    )
  })

  // Feature: frontend-coverage-extension, Property 2: Émission de suppression contient l'identifiant du document
  // **Validates: Requirements 3.3**
  it('should emit delete-document with the correct document ID for any ID (property-based)', async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 100000 }), async (docId) => {
        const w = mount(DocumentPatient, {
          props: {
            document: createMockDocument({ id_document: docId }),
            documentIndex: 0
          },
          global: {
            plugins: [i18n],
            stubs
          }
        })

        const buttons = w.findAll('button')
        const deleteButton = buttons.find((b: any) => b.text().includes('Supprimer'))
        await deleteButton!.trigger('click')

        const emitted = w.emitted('delete-document')
        const hasEmission = emitted !== undefined && emitted.length > 0
        const correctId = hasEmission && emitted![0][0] === docId

        w.unmount()

        return hasEmission && correctId
      }),
      { numRuns: 100 }
    )
  })
})
