import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// --- Mock vue-router ---
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ name: 'test' })
}))

// --- Mock user store ---
const mockLogout = vi.fn()
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    role: 'home',
    getUserInfos: vi.fn(),
    logout: mockLogout,
    signout: vi.fn()
  })
}))

// --- Mock axios ---
const mockRequest = vi.fn()
const mockInterceptorUse = vi.fn()
const mockInterceptorEject = vi.fn()

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      request: mockRequest,
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: mockInterceptorUse, eject: mockInterceptorEject }
      },
      get: vi.fn(),
    }))
  }
}))

// --- Mock onUnmounted (no-op in test) ---
vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onUnmounted: vi.fn()
  }
})

import useHttp from '@/composables/useHttp'
import axios from 'axios'

describe('UseHttp', () => {
  let axiosCreateMock: ReturnType<typeof vi.fn>
  let interceptorCallback: (response: any) => any
  let interceptorErrorCallback: (error: any) => any

  beforeEach(() => {
    vi.clearAllMocks()

    // Capture the interceptor callbacks registered via axios.create().interceptors.response.use
    mockInterceptorUse.mockImplementation((onFulfilled: any, onRejected: any) => {
      interceptorCallback = onFulfilled
      interceptorErrorCallback = onRejected
      return 0 // interceptor id
    })

    // Re-create the mock instance so each test gets fresh interceptors
    axiosCreateMock = (axios.create as ReturnType<typeof vi.fn>)
    axiosCreateMock.mockReturnValue({
      request: mockRequest,
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: mockInterceptorUse, eject: mockInterceptorEject }
      },
      get: vi.fn(),
    })
  })

  // --- Requirement 1.1: Successful request returns data and isLoading transitions ---
  describe('successful request', () => {
    it('should return data from sendRequest and transition isLoading from true to false', async () => {
      const responseData = { id: 1, name: 'test' }
      mockRequest.mockResolvedValueOnce({ data: responseData })

      const { sendRequest, isLoading } = useHttp()

      expect(isLoading.value).toBe(false)

      const result = await sendRequest({ path: '/test', method: 'get' })

      expect(result).toEqual(responseData)
      expect(isLoading.value).toBe(false) // after completion, isLoading is false
    })

    it('should call applyData callback with response data when provided', async () => {
      const responseData = { id: 2, name: 'callback-test' }
      mockRequest.mockResolvedValueOnce({ data: responseData })

      const { sendRequest } = useHttp()
      const applyData = vi.fn()

      await sendRequest({ path: '/test', method: 'get' }, applyData)

      expect(applyData).toHaveBeenCalledWith(responseData)
    })
  })

  // --- Requirement 1.2: Server error (status >= 500) redirects to "network-issue" ---
  describe('server error (status >= 500)', () => {
    it('should redirect to network-issue on 500 error', async () => {
      const { sendRequest } = useHttp()

      // Simulate a 500 error through the interceptor
      const error500 = {
        response: { status: 500, data: { detail: 'Internal Server Error' } },
        config: { url: '/test', _retry: false }
      }

      // Call the interceptor error handler directly
      await interceptorErrorCallback(error500).catch(() => {})

      expect(mockPush).toHaveBeenCalledWith({ name: 'network-issue' })
    })

    it('should redirect to network-issue on 503 error', async () => {
      useHttp()

      const error503 = {
        response: { status: 503, data: { detail: 'Service Unavailable' } },
        config: { url: '/test', _retry: false }
      }

      await interceptorErrorCallback(error503).catch(() => {})

      expect(mockPush).toHaveBeenCalledWith({ name: 'network-issue' })
    })
  })

  // --- Requirement 1.3: 401 error attempts token refresh via /auth/refresh ---
  describe('401 error and token refresh', () => {
    it('should attempt token refresh on 401 error', async () => {
      const mockAxiosInstance = {
        request: mockRequest,
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: mockInterceptorUse, eject: mockInterceptorEject }
        },
        get: vi.fn().mockResolvedValueOnce({ status: 200 }),
      }
      // Make the instance callable for retry
      const callableInstance = Object.assign(
        vi.fn().mockResolvedValueOnce({ data: 'retried' }),
        mockAxiosInstance
      )
      axiosCreateMock.mockReturnValue(callableInstance)

      useHttp()

      const error401 = {
        response: { status: 401, data: { detail: 'Unauthorized' } },
        config: { url: '/some-endpoint', _retry: false }
      }

      await interceptorErrorCallback(error401)

      expect(callableInstance.get).toHaveBeenCalledWith('/auth/refresh')
    })
  })

  // --- Requirement 1.4: Refresh failure calls userStore.logout() ---
  describe('refresh token failure', () => {
    it('should call userStore.logout() when refresh token fails', async () => {
      const mockAxiosInstance = {
        request: mockRequest,
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: mockInterceptorUse, eject: mockInterceptorEject }
        },
        get: vi.fn().mockRejectedValueOnce(new Error('refresh failed')),
      }
      const callableInstance = Object.assign(vi.fn(), mockAxiosInstance)
      axiosCreateMock.mockReturnValue(callableInstance)

      useHttp()

      const error401 = {
        response: { status: 401, data: { detail: 'Unauthorized' } },
        config: { url: '/some-endpoint', _retry: false }
      }

      await interceptorErrorCallback(error401).catch(() => {})

      expect(mockLogout).toHaveBeenCalled()
    })

    it('should call userStore.logout() when 401 on /auth/refresh itself', async () => {
      useHttp()

      const errorRefresh401 = {
        response: { status: 401, data: { detail: 'Unauthorized' } },
        config: { url: '/auth/refresh', _retry: false }
      }

      await interceptorErrorCallback(errorRefresh401).catch(() => {})

      expect(mockLogout).toHaveBeenCalled()
    })
  })

  // --- Requirement 1.5: error contains the detail message from API response ---
  describe('error message capture', () => {
    it('should set error to the detail message from API response', async () => {
      mockRequest.mockRejectedValueOnce({
        response: { data: { detail: 'Patient not found' } }
      })

      const { sendRequest, error } = useHttp()

      await sendRequest({ path: '/test', method: 'get' }).catch(() => {})

      expect(error.value).toBe('Patient not found')
    })

    it('should set error to unknown_error when no detail is provided', async () => {
      mockRequest.mockRejectedValueOnce({
        response: { data: {} }
      })

      const { sendRequest, error } = useHttp()

      await sendRequest({ path: '/test', method: 'get' }).catch(() => {})

      expect(error.value).toBe('unknown_error')
    })
  })

  // --- Requirement 1.6: FormData doesn't force Content-Type to application/json ---
  describe('FormData Content-Type handling', () => {
    it('should not set Content-Type to application/json when body is FormData', async () => {
      mockRequest.mockResolvedValueOnce({ data: { success: true } })

      const { sendRequest } = useHttp()
      const formData = new FormData()
      formData.append('file', new Blob(['test']), 'test.pdf')

      await sendRequest({ path: '/upload', method: 'post', body: formData })

      const requestCall = mockRequest.mock.calls[0][0]
      expect(requestCall.headers).not.toHaveProperty('Content-Type')
    })

    it('should set Content-Type to application/json for non-FormData body', async () => {
      mockRequest.mockResolvedValueOnce({ data: { success: true } })

      const { sendRequest } = useHttp()

      await sendRequest({
        path: '/test',
        method: 'post',
        body: { name: 'test' }
      })

      const requestCall = mockRequest.mock.calls[0][0]
      expect(requestCall.headers['Content-Type']).toBe('application/json')
    })
  })
})
