import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, config } from '@vue/test-utils'
import PatientForm from '@/components/create-update-patient/PatientForm.vue'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import PrimeVue from 'primevue/config'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { regexGeneric } from '@/libs/regex'

// Configuration i18n pour les tests
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr }
})

// Configuration globale pour les tests
config.global.stubs = {
  Transition: {
    template: '<slot></slot>'
  }
}

// Schéma de validation pour les tests
const testSchema = toTypedSchema(
  z.object({
    civilite: z
      .any()
      .transform((val) => {
        if (val && typeof val === 'object' && 'value' in val) {
          return val.value
        }
        return val
      })
      .pipe(
        z.enum(['Monsieur', 'Madame', 'Autre', 'Roberto'], {
          errorMap: () => ({ message: 'error.invalid_civility' })
        })
      ),
    date_de_naissance: z.union([
      z.string({
        required_error: 'error.no_birth_date'
      }),
      z.date({
        required_error: 'error.no_birth_date'
      })
    ]),
    prenom: z
      .string({ required_error: 'error.no_firstname' })
      .regex(regexGeneric, { message: 'error.not_valid_firstname' }),
    nom: z
      .string({ required_error: 'error.no_lastname' })
      .regex(regexGeneric, { message: 'error.not_valid_lastname' }),
    adresse: z
      .string({ required_error: 'error.no_address' })
      .regex(regexGeneric, { message: 'error.not_valid_address' }),
    code_postal: z
      .string({ required_error: 'error.no_zipcode' })
      .regex(regexGeneric, { message: 'error.not_valid_zipcode' }),
    ville: z
      .string({ required_error: 'error.no_city' })
      .regex(regexGeneric, { message: 'error.not_valid_city' }),
    telephone: z
      .string({ required_error: 'error.no_phone' })
      .regex(regexGeneric, { message: 'error.not_valid_phone' }),
    email: z.string().email({ message: 'error.not_valid_email' }).optional().nullable()
  })
)

describe('PatientForm', () => {
  // Props par défaut pour les tests
  const defaultProps = {
    patientDetail: undefined,
    civilites: ['Monsieur', 'Madame', 'Autre', 'Roberto'],
    onSubmit: vi.fn(),
    schema: testSchema,
    isLoading: false
  }

  let wrapper: any

  // Configuration initiale avant chaque test
  beforeEach(() => {
    wrapper = mount(PatientForm, {
      props: defaultProps,
      global: {
        plugins: [i18n, [PrimeVue, { ripple: true, inputStyle: 'filled' }]],
        stubs: {
          Field: {
            template:
              '<div><slot :field="{ value: modelValue, handleChange: (val) => $emit(\'update:modelValue\', val) }" /></div>',
            props: ['modelValue'],
            emits: ['update:modelValue']
          },
          'p-connected-overlay': {
            template: '<div><slot /></div>',
            emits: ['enter', 'afterEnter', 'leave', 'afterLeave']
          },
          Portal: true,
          Transition: false
        }
      }
    })
  })

  // Test de rendu du formulaire
  it('rend correctement le formulaire', () => {
    expect(wrapper.find('form').exists()).toBe(true)
  })

  // Test de présence de tous les champs requis
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

  // Test de la soumission du formulaire
  it('appelle onSubmit avec les données correctes lors de la soumission', async () => {
    const wrapper = mount(PatientForm, {
      props: defaultProps,
      global: {
        plugins: [i18n, PrimeVue],
        stubs: {
          'p-message': {
            template: '<div data-test="error-message"><slot></slot></div>'
          },
          'p-connected-overlay': true
        }
      }
    })

    // Remplir les champs du formulaire
    await wrapper.find('[data-test="civilite"]').setValue('Monsieur')
    await wrapper.find('[data-test="nom"]').setValue('Dupont')
    await wrapper.find('[data-test="prenom"]').setValue('Jean')
    await wrapper.find('[data-test="date_de_naissance"]').setValue(new Date('1990-01-01'))
    await wrapper.find('[data-test="adresse"]').setValue('1 rue de la Paix')
    await wrapper.find('[data-test="code_postal"]').setValue('75000')
    await wrapper.find('[data-test="ville"]').setValue('Paris')
    await wrapper.find('[data-test="telephone"]').setValue('0123456789')
    await wrapper.find('[data-test="email"]').setValue('test@test.com')

    // Soumettre le formulaire
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))
    // Vérifier que onSubmit a été appelé avec les bonnes données
    expect(defaultProps.onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        civilite: 'Monsieur',
        nom: 'Dupont',
        prenom: 'Jean',
        date_de_naissance: new Date('1990-01-01'),
        adresse: '1 rue de la Paix',
        code_postal: '75000',
        ville: 'Paris',
        telephone: '0123456789',
        email: 'test@test.com'
      })
    )
  })

  // Test du bouton de soumission pendant le chargement
  it('désactive le bouton de soumission pendant le chargement', async () => {
    const wrapper = mount(PatientForm, {
      props: { ...defaultProps, isLoading: true },
      global: {
        plugins: [i18n, PrimeVue]
      }
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  // Test de la validation des champs requis
  it("affiche les messages d'erreur pour les champs requis", async () => {
    const form = wrapper.find('form')
    await form.trigger('submit')

    // Attendre que la validation soit effectuée
    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Vérifier les messages d'erreur
    const errorMessages = wrapper.findAll('[data-test="error-message"]')
    expect(errorMessages.length).toBeGreaterThan(0)

    // Vérifier les messages spécifiques si nécessaire
    const errors = errorMessages.map((err: any) => err.text())
    expect(errors).toContain(expect.stringContaining('requis'))
  })

  // Test du pré-remplissage avec patientDetail
  it('pré-remplit le formulaire avec les données du patient', async () => {
    const patientDetail = {
      civilite: 'Monsieur',
      nom: 'Dupont',
      prenom: 'Jean',
      date_de_naissance: new Date('1990-01-01'),
      adresse: '1 rue de la Paix',
      code_postal: '75000',
      ville: 'Paris',
      telephone: '0123456789',
      email: 'jean.dupont@email.com'
    }

    const wrapper = mount(PatientForm, {
      props: {
        ...defaultProps,
        patientDetail: {
          ...patientDetail,
          id_patient: 1,
          date_de_naissance: patientDetail.date_de_naissance.toISOString(),
          documents: []
        }
      },
      global: {
        plugins: [i18n, PrimeVue]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.find('#civilite').element.getAttribute('value')).toBe(patientDetail.civilite)
    expect(wrapper.find('#nom').element.getAttribute('value')).toBe(patientDetail.nom)
    expect(wrapper.find('#prenom').element.getAttribute('value')).toBe(patientDetail.prenom)
    expect(wrapper.find('#date_de_naissance').element.getAttribute('value')).toBe(
      patientDetail.date_de_naissance.toISOString()
    )
    expect(wrapper.find('#adresse').element).toBeDefined()
    expect(wrapper.find('#adresse').element.getAttribute('value')).toBe(patientDetail.adresse)
    expect(wrapper.find('#code_postal').element).toBeDefined()
    expect(wrapper.find('#code_postal').element.getAttribute('value')).toBe(
      patientDetail.code_postal
    )
    expect(wrapper.find('#ville').element).toBeDefined()
    expect(wrapper.find('#ville').element.getAttribute('value')).toBe(patientDetail.ville)
    expect(wrapper.find('#telephone').element).toBeDefined()
    expect(wrapper.find('#telephone').element.getAttribute('value')).toBe(patientDetail.telephone)
    expect(wrapper.find('#email').element).toBeDefined()
    expect(wrapper.find('#email').element.getAttribute('value')).toBe(patientDetail.email)
  })

  // Test de la réinitialisation du formulaire
  it('réinitialise correctement le formulaire', async () => {
    // Remplir le formulaire
    await wrapper.find('#nom').setValue('Test')
    await wrapper.find('#prenom').setValue('Test')

    const form = wrapper.find('form')
    await form.trigger('reset')

    await wrapper.vm.$nextTick()

    // Vérifier que les champs sont vides
    expect(wrapper.find('#nom').element.value).toBe('')
    expect(wrapper.find('#prenom').element.value).toBe('')
  })
})
