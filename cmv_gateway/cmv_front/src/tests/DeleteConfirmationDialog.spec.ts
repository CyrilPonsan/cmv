import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import DeleteConfirmationDialog from '@/components/documents/DeleteConfirmationDialog.vue'
import { createI18n } from 'vue-i18n'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

// Configuration i18n
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr, en }
})

// Stubs PrimeVue
const stubs = {
  Dialog: {
    template:
      '<div class="dialog" v-if="visible"><slot /><slot name="footer" /></div>',
    props: ['visible', 'header'],
    emits: ['update:visible']
  },
  Button: {
    template:
      '<button :disabled="disabled" :loading="loading"><slot />{{ label }}</button>',
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

describe('DeleteConfirmationDialog', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(DeleteConfirmationDialog, {
      props: {
        document: createMockDocument(),
        visible: true,
        loading: false
      },
      global: {
        plugins: [i18n],
        stubs
      }
    })
  })

  it('affiche le type de document dans le dialogue', () => {
    const text = wrapper.text()
    expect(text).toContain('Autorisation de soins')
  })

  it('émet "confirm" lors du clic sur le bouton de confirmation', async () => {
    const buttons = wrapper.findAll('button')
    const confirmButton = buttons.find((b: any) => b.text().includes('Confirmer'))
    expect(confirmButton).toBeTruthy()
    await confirmButton!.trigger('click')
    expect(wrapper.emitted('confirm')).toBeTruthy()
    expect(wrapper.emitted('confirm')!.length).toBe(1)
  })

  it('émet "cancel" lors du clic sur le bouton d\'annulation', async () => {
    const buttons = wrapper.findAll('button')
    const cancelButton = buttons.find((b: any) => b.text().includes('Annuler'))
    expect(cancelButton).toBeTruthy()
    await cancelButton!.trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
    expect(wrapper.emitted('cancel')!.length).toBe(1)
  })

  it('affiche un état de chargement sur le bouton de confirmation quand loading=true', async () => {
    await wrapper.setProps({ loading: true })
    const buttons = wrapper.findAll('button')
    const confirmButton = buttons.find((b: any) => b.text().includes('Confirmer'))
    expect(confirmButton).toBeTruthy()
    expect(confirmButton!.attributes('loading')).toBe('true')
  })

  it('masque le bloc type de document quand document est null', () => {
    const wrapperNull = mount(DeleteConfirmationDialog, {
      props: {
        document: null,
        visible: true,
        loading: false
      },
      global: {
        plugins: [i18n],
        stubs
      }
    })
    const text = wrapperNull.text()
    expect(text).not.toContain('Autorisation de soins')
    // The v-if="document" div should not be rendered
    expect(wrapperNull.find('.font-bold.opacity-50').exists()).toBe(false)
  })
})
