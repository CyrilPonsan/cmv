import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PatientForm from '@/components/create-update-patient/PatientForm.vue'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import PrimeVue from 'primevue/config'

// Mock des composants PrimeVue
vi.mock('primevue/inputtext', () => ({
  default: {
    name: 'InputText',
    template:
      '<input type="text" v-bind="$attrs" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    inheritAttrs: false
  }
}))

vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button type="submit" :disabled="loading"><slot /></button>',
    props: ['loading']
  }
}))

vi.mock('primevue/datepicker', () => ({
  default: {
    name: 'DatePicker',
    template: '<input type="date" @update:modelValue="$emit(\'update:modelValue\', $event)" />',
    props: ['modelValue']
  }
}))

vi.mock('primevue/select', () => ({
  default: {
    name: 'Select',
    template:
      '<select @change="$emit(\'update:modelValue\', $event.target.value)"><option v-for="opt in options" :value="opt">{{ opt }}</option></select>',
    props: ['modelValue', 'options']
  }
}))

vi.mock('primevue/textarea', () => ({
  default: {
    name: 'Textarea',
    template: '<textarea @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue']
  }
}))

vi.mock('primevue/message', () => ({
  default: {
    name: 'Message',
    template: '<div class="p-message" :severity="severity"><slot /></div>',
    props: ['severity']
  }
}))

// Configuration i18n
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr }
})

// Schéma de validation pour les tests
const testSchema = toTypedSchema(
  z.object({
    civilite: z.string(),
    nom: z.string().min(1, 'Le nom est requis'),
    prenom: z.string().min(1, 'Le prénom est requis'),
    adresse: z.string(),
    code_postal: z.string(),
    ville: z.string(),
    telephone: z.string(),
    email: z.string().email('Email invalide').optional().nullable()
  })
)

describe('PatientForm', () => {
  const mockProps = {
    civilite: 'M.',
    civilites: ['M.', 'Mme', 'Autre'],
    date_de_naissance: new Date('1990-01-01'),
    onSubmit: vi.fn(),
    schema: testSchema,
    isLoading: false,
    updateCivilite: vi.fn(),
    updateDateDeNaissance: vi.fn()
  }

  let wrapper: any

  beforeEach(() => {
    wrapper = mount(PatientForm, {
      props: mockProps,
      global: {
        plugins: [
          i18n,
          [
            PrimeVue,
            {
              ripple: true,
              inputStyle: 'filled'
            }
          ]
        ],
        stubs: {
          Field: {
            template: '<div><slot :field="{ value: \'\' }" /></div>'
          }
        }
      }
    })
  })

  it('rend correctement le formulaire', () => {
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('affiche correctement les champs du formulaire', () => {
    expect(wrapper.find('label[for="civilite"]').exists()).toBe(true)
    expect(wrapper.find('label[for="date_de_naissance"]').exists()).toBe(true)
    expect(wrapper.find('label[for="nom"]').exists()).toBe(true)
    expect(wrapper.find('label[for="prenom"]').exists()).toBe(true)
    expect(wrapper.find('label[for="adresse"]').exists()).toBe(true)
    expect(wrapper.find('label[for="code_postal"]').exists()).toBe(true)
    expect(wrapper.find('label[for="ville"]').exists()).toBe(true)
    expect(wrapper.find('label[for="telephone"]').exists()).toBe(true)
    expect(wrapper.find('label[for="email"]').exists()).toBe(true)
  })

  it('appelle updateCivilite lors du changement de civilité', async () => {
    const select = wrapper.findComponent({ name: 'Select' })
    await select.vm.$emit('update:modelValue', 'Mme')
    expect(mockProps.updateCivilite).toHaveBeenCalledWith('Mme')
  })

  it('appelle updateDateDeNaissance lors du changement de date', async () => {
    const datePicker = wrapper.findComponent({ name: 'DatePicker' })
    const newDate = new Date('1995-01-01')
    await datePicker.vm.$emit('update:modelValue', newDate)
    expect(mockProps.updateDateDeNaissance).toHaveBeenCalledWith(newDate)
  })

  it('appelle onSubmit avec les données correctes lors de la soumission', async () => {
    const form = wrapper.find('form')
    const testData = {
      civilite: 'M.',
      nom: 'Dupont',
      prenom: 'Jean',
      date_de_naissance: new Date('1990-01-01'),
      adresse: '1 rue de la Paix',
      code_postal: '75000',
      ville: 'Paris',
      telephone: '0123456789',
      email: 'jean.dupont@email.com'
    }

    // Remplir le formulaire
    Object.entries(testData).forEach(async ([key, value]) => {
      const input = wrapper.find(`[name="${key}"]`)
      if (input.exists()) {
        await input.setValue(value)
      }
    })

    // Soumettre le formulaire
    await form.trigger('submit')

    // Vérifier que onSubmit a été appelé avec les bonnes données
    expect(mockProps.onSubmit).toHaveBeenCalledWith(expect.objectContaining(testData))
  })

  it('désactive le bouton de soumission pendant le chargement', async () => {
    const loadingWrapper = mount(PatientForm, {
      props: {
        ...mockProps,
        isLoading: true
      },
      global: {
        plugins: [i18n]
      }
    })

    const submitButton = loadingWrapper.findComponent({ name: 'Button' })
    expect(submitButton.props('loading')).toBe(true)
  })

  it("affiche les messages d'erreur pour les champs requis", async () => {
    const form = wrapper.find('form')
    await form.trigger('submit')

    // Vérifier que les messages d'erreur sont affichés
    const errorMessages = wrapper.findAll('.p-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })
})
