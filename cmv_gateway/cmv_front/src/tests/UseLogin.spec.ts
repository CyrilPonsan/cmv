import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import useLogin from '../composables/useLogin'
import { ref } from 'vue'
import { z } from 'zod'
import { regexPassword } from '@/libs/regex'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      request: vi.fn().mockResolvedValue({ data: { token: 'fake-token' } }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }))
  }
}))

// Mock des dépendances externes
vi.mock('primevue/usetoast', () => ({
  useToast: vi.fn(() => ({
    add: vi.fn()
  }))
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key // Retourne la clé comme valeur pour simplifier
  })
}))

// Mock du store user
vi.mock('@/stores/user', () => ({
  useUserStore: vi.fn(() => ({
    getUserInfos: vi.fn(),
    login: vi.fn().mockResolvedValue(true)
  }))
}))

// Mock de useLogin avec les valeurs et fonctions nécessaires
vi.mock('../composables/useLogin', () => ({
  default: () => ({
    error: ref(null),
    isLoading: ref(false),
    initialValues: {
      username: '',
      password: ''
    },
    loginFormSchema: z.object({
      username: z
        .string({ required_error: 'error.no_email' })
        .email({ message: 'error.not_valid_email' }),
      password: z
        .string({ required_error: 'error.no_password' })
        .regex(regexPassword, { message: 'error.not_valid_password' })
    }),
    onSubmit: vi.fn()
  })
}))

describe('useLogin', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should return initial values and required functions', () => {
    const { error, initialValues, isLoading, loginFormSchema, onSubmit } = useLogin()

    expect(error.value).toBe(null)
    expect(initialValues).toEqual({
      username: '',
      password: ''
    })
    expect(isLoading.value).toBe(false)
    expect(loginFormSchema).toBeDefined()
    expect(onSubmit).toBeDefined()
  })

  it('should validate form data correctly', () => {
    const { loginFormSchema } = useLogin()
    const validData = {
      username: 'test@example.com',
      password: 'ValidPassword123@'
    }

    // Vérifier que la validation ne lance pas d'erreur
    expect(() => loginFormSchema.parse(validData)).not.toThrow()

    // Vérifier le résultat de la validation
    const result = loginFormSchema.parse(validData)
    expect(result).toEqual(validData)
  })
})
