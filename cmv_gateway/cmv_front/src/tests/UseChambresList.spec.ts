import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// --- Mock vue-router ---
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ name: 'test' })
}))

// --- Mock user store ---
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    role: 'home',
    getUserInfos: vi.fn(),
    logout: vi.fn(),
    signout: vi.fn()
  })
}))

// --- Mock useHttp ---
const mockSendRequest = vi.fn()
const mockError = ref<string | null>(null)
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: mockSendRequest,
    isLoading: ref(false),
    error: mockError,
    axiosInstance: {}
  })
}))

// --- Mock lifecycle hooks (no-op in test) ---
vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onBeforeMount: vi.fn((cb: () => void) => cb()),
    onUnmounted: vi.fn()
  }
})

import useChambresList from '@/composables/useChambresList'

const mockServices = [
  { id_service: 1, nom: 'Cardiologie', chambres: [] },
  { id_service: 2, nom: 'Chirurgie', chambres: [] },
  { id_service: 3, nom: 'cardiologie pédiatrique', chambres: [] },
  { id_service: 4, nom: 'Neurologie', chambres: [] }
]

/**
 * Helper: simulate getChambres populating the initial list
 * by invoking the applyData callback passed to sendRequest.
 */
function simulateGetChambres(services = mockServices) {
  mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
    if (req.path === '/chambres/services') {
      applyData(services)
    }
  })
}

describe('UseChambresList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockError.value = null
    mockSendRequest.mockReset()
  })

  // --- Requirement 3.1: GET call to /chambres/services ---
  describe('getChambres', () => {
    it('should call sendRequest with /chambres/services', () => {
      simulateGetChambres()
      useChambresList()

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/chambres/services' },
        expect.any(Function)
      )
    })

    it('should populate list with data returned from API', async () => {
      simulateGetChambres()
      const { list } = useChambresList()

      await new Promise((r) => setTimeout(r, 0))
      expect(list.value).toEqual(mockServices)
    })

    it('should populate suggestions with service names', async () => {
      simulateGetChambres()
      const { suggestions } = useChambresList()

      await new Promise((r) => setTimeout(r, 0))
      expect(suggestions.value).toEqual(
        mockServices.map((s) => s.nom)
      )
    })
  })

  // --- Requirement 3.2: Case-insensitive prefix filtering via search ---
  describe('search (case-insensitive prefix filtering)', () => {
    it('should filter suggestions by case-insensitive prefix', () => {
      simulateGetChambres()
      const { search, suggestions } = useChambresList()

      search({ query: 'car' } as any)

      expect(suggestions.value).toEqual(['Cardiologie', 'cardiologie pédiatrique'])
    })

    it('should filter list by case-insensitive prefix', () => {
      simulateGetChambres()
      const { search, list } = useChambresList()

      search({ query: 'Car' } as any)

      expect(list.value).toEqual([
        { id_service: 1, nom: 'Cardiologie', chambres: [] },
        { id_service: 3, nom: 'cardiologie pédiatrique', chambres: [] }
      ])
    })

    it('should match uppercase query against lowercase service names', () => {
      simulateGetChambres()
      const { search, list } = useChambresList()

      search({ query: 'NEURO' } as any)

      expect(list.value).toEqual([
        { id_service: 4, nom: 'Neurologie', chambres: [] }
      ])
    })
  })

  // --- Requirement 3.3: Reset list when search finds nothing ---
  describe('search reset when no results', () => {
    it('should reset list to initial list when search finds no matches', () => {
      simulateGetChambres()
      const { search, list } = useChambresList()

      search({ query: 'zzz_no_match' } as any)

      expect(list.value).toEqual(mockServices)
    })

    it('should set suggestions to empty when search finds no matches', () => {
      simulateGetChambres()
      const { search, suggestions } = useChambresList()

      search({ query: 'zzz_no_match' } as any)

      expect(suggestions.value).toEqual([])
    })
  })

  // --- Requirement 3.4: searchBySelect updates searchValue and filters by exact prefix ---
  describe('searchBySelect', () => {
    it('should update searchValue with the selected value', () => {
      simulateGetChambres()
      const { searchBySelect, searchValue } = useChambresList()

      searchBySelect({ value: 'Cardiologie' } as any)

      expect(searchValue.value).toBe('Cardiologie')
    })

    it('should filter list by exact (case-sensitive) prefix', () => {
      simulateGetChambres()
      const { searchBySelect, list } = useChambresList()

      searchBySelect({ value: 'Cardiologie' } as any)

      expect(list.value).toEqual([
        { id_service: 1, nom: 'Cardiologie', chambres: [] }
      ])
    })

    it('should not match case-insensitively for searchBySelect', () => {
      simulateGetChambres()
      const { searchBySelect, list } = useChambresList()

      // 'cardiologie' lowercase should only match the lowercase service
      searchBySelect({ value: 'cardiologie' } as any)

      expect(list.value).toEqual([
        { id_service: 3, nom: 'cardiologie pédiatrique', chambres: [] }
      ])
    })
  })

  // --- Requirement 3.5: resetSearchValue ---
  describe('resetSearchValue', () => {
    it('should reset searchValue to empty string', () => {
      simulateGetChambres()
      const { searchBySelect, resetSearchValue, searchValue } = useChambresList()

      searchBySelect({ value: 'Cardiologie' } as any)
      expect(searchValue.value).toBe('Cardiologie')

      resetSearchValue()
      expect(searchValue.value).toBe('')
    })
  })

  // --- Requirement 3.6: Reset when searchValue is emptied ---
  describe('reset when searchValue is emptied', () => {
    it('should reset list to initial list when searchValue becomes empty', async () => {
      simulateGetChambres()
      const { searchBySelect, searchValue, list } = useChambresList()

      // Filter first
      searchBySelect({ value: 'Cardiologie' } as any)
      expect(list.value.length).toBe(1)

      // Empty searchValue triggers the watcher
      searchValue.value = ''
      await new Promise((r) => setTimeout(r, 0))

      expect(list.value).toEqual(mockServices)
    })

    it('should reset suggestions to all service names when searchValue becomes empty', async () => {
      simulateGetChambres()
      const { searchBySelect, searchValue, suggestions } = useChambresList()

      searchBySelect({ value: 'Cardiologie' } as any)

      searchValue.value = ''
      await new Promise((r) => setTimeout(r, 0))

      expect(suggestions.value).toEqual(mockServices.map((s) => s.nom))
    })
  })
})
