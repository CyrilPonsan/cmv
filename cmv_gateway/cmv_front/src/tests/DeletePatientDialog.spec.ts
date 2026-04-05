import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DeletePatientDialog from '@/components/DeletePatientDialog.vue'
import { createI18n } from 'vue-i18n'
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

const createMockPatient = (overrides = {}) => ({
  id_patient: 1,
  nom: 'Dupont',
  prenom: 'Jean',
  date_de_naissance: '1990-01-15',
  telephone: '0123456789',
  ...overrides
})

describe('DeletePatientDialog', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(DeletePatientDialog, {
      props: {
        patient: createMockPatient(),
        visible: true
      },
      global: {
        plugins: [i18n],
        stubs
      }
    })
  })

  it('affiche le nom, le prénom et la date de naissance du patient', () => {
    const text = wrapper.text()
    expect(text).toContain('Dupont')
    expect(text).toContain('Jean')
    // Date formatted by i18n 'short' format for fr locale: 15/01/1990
    expect(text).toContain('15/01/1990')
  })

  it('émet "confirm" lors du clic sur le bouton Confirmer', async () => {
    const buttons = wrapper.findAll('button')
    const confirmButton = buttons.find((b: any) => b.text().includes('Confirmer'))
    expect(confirmButton).toBeTruthy()
    await confirmButton!.trigger('click')
    expect(wrapper.emitted('confirm')).toBeTruthy()
    expect(wrapper.emitted('confirm')!.length).toBe(1)
  })

  it('émet "cancel" lors du clic sur le bouton Annuler', async () => {
    const buttons = wrapper.findAll('button')
    const cancelButton = buttons.find((b: any) => b.text().includes('Annuler'))
    expect(cancelButton).toBeTruthy()
    await cancelButton!.trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
    expect(wrapper.emitted('cancel')!.length).toBe(1)
  })

  it('émet "cancel" quand le Dialog est fermé via update:visible', async () => {
    const dialog = wrapper.findComponent(stubs.Dialog)
    await dialog.vm.$emit('update:visible', false)
    expect(wrapper.emitted('cancel')).toBeTruthy()
    expect(wrapper.emitted('cancel')!.length).toBe(1)
  })
})
