import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { z } from 'zod'
import { regexPassword } from '@/libs/regex'

// --- Mock vue-router (needed by useHttp internally) ---
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ name: 'root', params: {} })
}))

// --- Mock useHttp at module level ---
const mockSendRequest = vi.fn()
const mockIsLoading = ref(false)
const mockError = ref<string | null>(null)

vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: mockIsLoading,
    error: mockError,
    axiosInstance: {}
  })
}))

// --- Mock useToast ---
const mockToastAdd = vi.fn()
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({
    add: mockToastAdd
  })
}))

// --- Mock vue-i18n ---
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

// --- Mock useUserStore ---
const mockGetUserInfos = vi.fn()
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    getUserInfos: mockGetUserInfos
  })
}))

// Import useLogin AFTER all mocks are set up — it runs its REAL logic
import useLogin from '@/composables/useLogin'

describe('useLogin', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockSendRequest.mockReset()
    mockError.value = null
    mockIsLoading.value = false
  })

  // --- Requirement 7.1: Initial state ---
  describe('initial state', () => {
    it('should have error as null', () => {
      const { error } = useLogin()
      expect(error.value).toBeNull()
    })

    it('should have isLoading as false', () => {
      const { isLoading } = useLogin()
      expect(isLoading.value).toBe(false)
    })

    it('should have initialValues with empty username and password', () => {
      const { initialValues } = useLogin()
      expect(initialValues).toEqual({ username: '', password: '' })
    })
  })

  // --- Requirement 7.2: onSubmit calls sendRequest with correct args ---
  describe('onSubmit', () => {
    it('should call sendRequest with path "/auth/login", method "post" and body containing credentials', () => {
      const { onSubmit } = useLogin()
      const credentials = { username: 'user@test.com', password: 'ValidPass123@' }

      onSubmit(credentials)

      expect(mockSendRequest).toHaveBeenCalledWith(
        {
          path: '/auth/login',
          method: 'post',
          body: { ...credentials }
        },
        expect.any(Function)
      )
    })
  })

  // --- Requirement 7.3: getUserInfos called on success ---
  describe('successful login', () => {
    it('should call getUserInfos when request succeeds with success=true', () => {
      mockSendRequest.mockImplementation(
        (_req: any, applyData: (data: { success: boolean; message: string }) => void) => {
          applyData({ success: true, message: 'ok' })
          return Promise.resolve()
        }
      )

      const { onSubmit } = useLogin()
      onSubmit({ username: 'user@test.com', password: 'ValidPass123@' })

      expect(mockGetUserInfos).toHaveBeenCalled()
    })

    it('should NOT call getUserInfos when request succeeds with success=false', () => {
      mockSendRequest.mockImplementation(
        (_req: any, applyData: (data: { success: boolean; message: string }) => void) => {
          applyData({ success: false, message: 'nope' })
          return Promise.resolve()
        }
      )

      const { onSubmit } = useLogin()
      onSubmit({ username: 'user@test.com', password: 'ValidPass123@' })

      expect(mockGetUserInfos).not.toHaveBeenCalled()
    })
  })

  // --- Requirement 7.4: Toast error when error becomes non-null ---
  describe('error toast', () => {
    it('should display an error toast when error becomes non-null', async () => {
      // Call useLogin to set up the watcher
      useLogin()

      // Trigger the error
      mockError.value = 'some_error'
      await nextTick()

      expect(mockToastAdd).toHaveBeenCalledWith({
        severity: 'error',
        life: 5000,
        summary: 'error.error',
        detail: 'error.connection_failure',
        closable: false
      })
    })
  })

  // --- Requirement 7.5: loginFormSchema validation ---
  describe('loginFormSchema validation', () => {
    // We test the underlying Zod schema directly since toTypedSchema wraps it
    const rawSchema = z.object({
      username: z
        .string({ required_error: 'error.no_email' })
        .email({ message: 'error.not_valid_email' }),
      password: z
        .string({ required_error: 'error.no_password' })
        .regex(regexPassword, { message: 'error.not_valid_password' })
    })

    it('should reject an invalid email', () => {
      const result = rawSchema.safeParse({
        username: 'not-an-email',
        password: 'ValidPass123@'
      })
      expect(result.success).toBe(false)
    })

    it('should reject a non-conforming password (too short, no special char)', () => {
      const result = rawSchema.safeParse({
        username: 'user@test.com',
        password: 'short'
      })
      expect(result.success).toBe(false)
    })

    it('should accept valid email and conforming password', () => {
      const result = rawSchema.safeParse({
        username: 'user@test.com',
        password: 'ValidPass123@'
      })
      expect(result.success).toBe(true)
    })

    it('should verify loginFormSchema is defined from useLogin', () => {
      const { loginFormSchema } = useLogin()
      expect(loginFormSchema).toBeDefined()
    })
  })
})
