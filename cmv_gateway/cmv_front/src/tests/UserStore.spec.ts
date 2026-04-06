import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { setActivePinia } from 'pinia'
import { createTestingPinia } from '@pinia/testing'

/** Safely remove a key from localStorage, compatible with all happy-dom versions */
function safeStorageRemove(key: string) {
  try {
    localStorage.removeItem(key)
  } catch {
    try { delete (localStorage as any)[key] } catch { /* noop */ }
  }
}

// --- Mock vue-router ---
const mockPush = vi.fn()
const mockRoute = { name: 'accueil', params: {} }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => mockRoute
}))

// --- Mock useHttp ---
const mockSendRequest = vi.fn()
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: ref(null),
    axiosInstance: {}
  })
}))

import { useUserStore } from '@/stores/user'

describe('UserStore', () => {
  let store: ReturnType<typeof useUserStore>

  beforeEach(() => {
    vi.clearAllMocks()
    mockSendRequest.mockReset()
    mockPush.mockReset()
    mockRoute.name = 'accueil'

    const pinia = createTestingPinia({
      createSpy: vi.fn,
      stubActions: false
    })
    setActivePinia(pinia)
    store = useUserStore()
  })

  // --- Requirement 13.1: Initial state ---
  describe('initial state', () => {
    it('should have role as empty string', () => {
      expect(store.role).toBe('')
    })

    it('should have mode as "light"', () => {
      expect(store.mode).toBe('light')
    })

    it('should have authChecked as false', () => {
      expect(store.authChecked).toBe(false)
    })
  })

  // --- Requirement 13.2: getUserInfos success ---
  describe('getUserInfos success', () => {
    it('should update role and set authChecked to true on success', () => {
      mockSendRequest.mockImplementation(
        (req: any, applyData: (data: { role: string }) => void) => {
          applyData({ role: 'home' })
          return Promise.resolve()
        }
      )

      store.getUserInfos()

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/users/me' },
        expect.any(Function)
      )
      expect(store.role).toBe('home')
      expect(store.authChecked).toBe(true)
    })
  })

  // --- Requirement 13.3: getUserInfos failure ---
  describe('getUserInfos failure', () => {
    it('should set authChecked to true even when the request fails', async () => {
      mockSendRequest.mockImplementation(() => {
        return Promise.reject(new Error('Network error'))
      })

      store.getUserInfos()

      // Wait for the catch handler to execute
      await vi.waitFor(() => {
        expect(store.authChecked).toBe(true)
      })
    })
  })

  // --- Requirement 13.4: signout ---
  describe('signout', () => {
    it('should reset role to empty string', () => {
      store.role = 'home'
      mockSendRequest.mockReturnValue(Promise.resolve())

      store.signout()

      expect(store.role).toBe('')
    })

    it('should send POST request to /auth/logout', () => {
      store.role = 'home'
      mockSendRequest.mockReturnValue(Promise.resolve())

      store.signout()

      expect(mockSendRequest).toHaveBeenCalledWith({
        path: '/auth/logout',
        method: 'post'
      })
    })

    it('should redirect to root when current route is not root', () => {
      store.role = 'home'
      mockRoute.name = 'accueil'
      mockSendRequest.mockReturnValue(Promise.resolve())

      store.signout()

      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('should not redirect when already on root route', () => {
      store.role = 'home'
      mockRoute.name = 'root'
      mockSendRequest.mockReturnValue(Promise.resolve())

      store.signout()

      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  // --- Requirement 13.5: logout ---
  describe('logout', () => {
    it('should reset role to empty string', () => {
      store.role = 'home'

      store.logout()

      expect(store.role).toBe('')
    })

    it('should redirect to root route when not already on root', () => {
      store.role = 'home'
      mockRoute.name = 'accueil'

      store.logout()

      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('should not redirect when already on root route', () => {
      store.role = 'home'
      mockRoute.name = 'root'

      store.logout()

      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  // --- Requirement 8.1, 8.2: toggleColorScheme ---
  describe('toggleColorScheme', () => {
    let htmlElement: HTMLElement

    beforeEach(() => {
      htmlElement = document.querySelector('html')!
      htmlElement.classList.remove('dark')
      safeStorageRemove('color-scheme')
      store.mode = 'light'
    })

    it('should add "dark" class to html, set mode to "dark" and update localStorage when toggling from light', () => {
      store.toggleColorScheme()

      expect(htmlElement.classList.contains('dark')).toBe(true)
      expect(store.mode).toBe('dark')
      expect(localStorage.getItem('color-scheme')).toBe('dark')
    })

    it('should remove "dark" class from html, set mode to "light" and clear localStorage when toggling from dark', () => {
      // Start in dark mode
      htmlElement.classList.add('dark')
      store.mode = 'dark'
      localStorage.setItem('color-scheme', 'dark')

      store.toggleColorScheme()

      expect(htmlElement.classList.contains('dark')).toBe(false)
      expect(store.mode).toBe('light')
      expect(localStorage.getItem('color-scheme')).toBeNull()
    })
  })

  // --- Requirement 8.3, 8.4: updateColorScheme (tested via handshake since updateColorScheme is internal) ---
  describe('updateColorScheme', () => {
    let htmlElement: HTMLElement

    beforeEach(() => {
      htmlElement = document.querySelector('html')!
      htmlElement.classList.remove('dark')
      safeStorageRemove('color-scheme')
      store.mode = 'light'
      mockSendRequest.mockReturnValue(Promise.resolve())
    })

    it('should set mode to "dark" and add "dark" class when localStorage contains "dark"', () => {
      localStorage.setItem('color-scheme', 'dark')

      // handshake calls updateColorScheme internally
      store.handshake()

      expect(store.mode).toBe('dark')
      expect(htmlElement.classList.contains('dark')).toBe(true)
    })

    it('should keep mode as "light" when localStorage does not contain "color-scheme"', () => {
      // handshake calls updateColorScheme internally
      store.handshake()

      expect(store.mode).toBe('light')
      expect(htmlElement.classList.contains('dark')).toBe(false)
    })
  })

  // --- Requirement 8.5: handshake ---
  describe('handshake', () => {
    beforeEach(() => {
      const htmlElement = document.querySelector('html')!
      htmlElement.classList.remove('dark')
      safeStorageRemove('color-scheme')
      store.mode = 'light'
    })

    it('should execute updateColorScheme and getUserInfos', () => {
      localStorage.setItem('color-scheme', 'dark')
      mockSendRequest.mockImplementation(
        (req: any, applyData?: (data: { role: string }) => void) => {
          if (applyData) applyData({ role: 'home' })
          return Promise.resolve()
        }
      )

      store.handshake()

      // updateColorScheme was executed: mode should be "dark"
      expect(store.mode).toBe('dark')
      // getUserInfos was executed: sendRequest called with /users/me
      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/users/me' },
        expect.any(Function)
      )
    })
  })
})
