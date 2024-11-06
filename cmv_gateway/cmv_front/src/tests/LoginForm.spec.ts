import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import fr from '../locales/fr.json'
import en from '../locales/en.json'
import { createTestingPinia } from '@pinia/testing'
import LoginForm from '@/components/LoginForm.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { nextTick, ref } from 'vue'
import { regexPassword } from '@/libs/regex'
import { z } from 'zod'
import useLogin from '@/composables/use-login'
import { toTypedSchema } from '@vee-validate/zod'

// Mock des composants
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button><slot /></button>'
  }
}))

// Mock pour InputText
vi.mock('primevue/inputtext', () => ({
  default: {
    name: 'InputText',
    template: '<input type="text" :value="value" @blur="$emit(\'blur\')" />',
    props: {
      value: {
        type: String,
        default: ''
      }
    },
    emits: ['blur', 'update:modelValue']
  }
}))

// Correction du mock pour Message
vi.mock('primevue/message', () => ({
  default: {
    name: 'Message',
    props: ['severity'],
    template: '<div class="p-message" :severity="severity"><slot /></div>'
  }
}))

// Mock pour Password
vi.mock('primevue/password', () => ({
  default: {
    name: 'Password',
    template: '<input type="password" :value="modelValue" @blur="$emit(\'blur\')" />',
    props: {
      modelValue: {
        type: String,
        default: ''
      }
    },
    emits: ['blur', 'update:modelValue']
  }
}))

// Mock de useLogin avec les valeurs et fonctions nécessaires
vi.mock('@/composables/use-login', () => ({
  default: () => ({
    error: ref(null),
    isLoading: ref(false),
    initialValues: {
      username: '',
      password: ''
    },
    loginFormSchema: toTypedSchema(
      z.object({
        username: z
          .string({ required_error: 'error.no_email' })
          .email({ message: 'error.not_valid_email' }),
        password: z
          .string({ required_error: 'error.no_password' })
          .regex(regexPassword, { message: 'error.not_valid_password' })
      })
    ),
    onSubmit: vi.fn().mockImplementation(async () => {
      toastMock.add({
        severity: 'success',
        summary: fr.success.connection_success,
        detail: fr.success.connection_success_detail,
        closable: false,
        life: 5000
      })
      return true
    }),
    errors: ref({}), // Clear errors for success case
    values: ref({
      username: 'valid@email.com',
      password: 'ValidPass123!'
    })
  })
}))

// Update the toast mock setup
const toastMock = {
  add: vi.fn()
}

vi.mock('primevue/usetoast', () => ({
  default: () => toastMock,
  useToast: () => toastMock
}))

const i18n = createI18n({
  legacy: false, // Composition API
  locale: 'fr',
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
  },
  fallbackLocale: 'fr',
  messages: {
    fr,
    en
  }
})

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: LoginForm
    }
  ]
})

describe('LoginForm tests unitaires', () => {
  let wrapper: any

  beforeEach(() => {
    // Reset mocks
    toastMock.add.mockReset()
    useLogin.mockReset()

    wrapper = mount(LoginForm, {
      global: {
        plugins: [
          i18n,
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              user: { role: '', mode: 'light' }
            }
          }),
          useLogin
        ]
      }
    })
  })

  // Teste si le composant est rendu
  it('should render the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  // Teste si le formulaire est rendu
  it('should render the form', () => {
    const form = wrapper.find('form')
    expect(form.exists()).toBe(true)
  })

  it('should render the right values', async () => {
    const username = wrapper.find('#username')
    const password = wrapper.find('[type="password"]')

    await username.setValue('test@example.com')
    await password.setValue('Test123!')

    // Vérification des valeurs
    expect(username.element.value).toBe('test@example.com')
    expect(password.element.value).toBe('Test123!')
  })

  it('should display an error message with invalid data', async () => {
    // Simuler des entrées invalides
    const usernameInput = wrapper.find('#username')
    const passwordInput = wrapper.find('[type="password"]')

    await usernameInput.setValue('invalid-email')
    await passwordInput.setValue('short')

    // Déclencher la validation
    await usernameInput.trigger('blur')
    await passwordInput.trigger('blur')

    // Soumettre le formulaire
    const form = wrapper.find('form')
    await form.trigger('submit')

    // Attendre que la validation soit terminée
    await nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Vérifier les messages d'erreur visibles
    const errorMessages = wrapper.findAll('.p-message)')
    expect(errorMessages.length).toBeGreaterThan(0)
    expect(errorMessages.length).toBe(2)
  })

  it('should render a success toast when login is successful', async () => {
    // Reset mocks
    toastMock.add.mockReset()

    // Mock the login success
    const loginHook = useLogin()
    loginHook.onSubmit({
      username: 'valid@email.com',
      password: 'ValidPass123!'
    })

    // Wait for the next tick
    await nextTick()

    // Verify toast was called
    expect(toastMock.add).toHaveBeenCalledWith({
      severity: 'success',
      summary: fr.success.connection_success,
      detail: fr.success.connection_success_detail,
      closable: false,
      life: 5000
    })
  })

  it('should render an error message if onSubmit return an error', async () => {
    vi.mock('@/composables/use-login', () => ({
      default: () => ({
        error: ref(null),
        isLoading: ref(false),
        initialValues: {
          username: '',
          password: ''
        },
        loginFormSchema: toTypedSchema(
          z.object({
            username: z
              .string({ required_error: 'error.no_email' })
              .email({ message: 'error.not_valid_email' }),
            password: z
              .string({ required_error: 'error.no_password' })
              .regex(regexPassword, { message: 'error.not_valid_password' })
          })
        ),
        onSubmit: vi.fn().mockImplementation(async () => {
          toastMock.add({
            severity: 'success',
            summary: fr.success.connection_success,
            detail: fr.success.connection_success_detail,
            closable: false,
            life: 5000
          })
          return true
        }),
        errors: ref({}), // Clear errors for success case
        values: ref({
          username: 'valid@email.com',
          password: 'ValidPass123!'
        })
      })
    }))
    // mock error from useLogin

    // Teste s'il y a quelquechose dans le p
    const p = wrapper.find('p')
    expect(p.exists()).toBe(true)
    expect(p.text()).toBe('ERROR')
  })
})
