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

// --- Mock services store ---
const mockServicesList = ref([
  { id_service: 1, nom: 'Cardiologie' },
  { id_service: 2, nom: 'Chirurgie' },
  { id_service: 3, nom: 'cardiologie pédiatrique' },
  { id_service: 4, nom: 'Neurologie' }
])
vi.mock('@/stores/services', () => ({
  useServices: () => ({
    servicesList: mockServicesList,
    servicesOptions: mockServicesList.value.map((s: { nom: string }) => s.nom),
    fetchServices: vi.fn()
  })
}))

// --- Mock pinia storeToRefs ---
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({
    servicesList: store.servicesList
  }),
  defineStore: vi.fn(),
  createPinia: vi.fn()
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

// Mock data: what the API returns for a given service_id
const mockServiceResponse = [
  { id_service: 1, nom: 'Cardiologie', chambres: [{ id_chambre: 1, nom: 'C101', status: 'libre', dernier_nettoyage: '2026-01-01' }] }
]

/**
 * Helper: simulate getChambres populating the list.
 * The composable now calls /chambres-liste/services/{serviceId}.
 * This mock intercepts any path matching that pattern and returns the response.
 */
function simulateGetChambres(response = mockServiceResponse) {
  mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
    if (req.path && req.path.startsWith('/chambres-liste/services/')) {
      applyData(response)
    }
  })
}

describe('UseChambresList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockError.value = null
    mockSendRequest.mockReset()
  })

  // --- getChambres with serviceId ---
  describe('getChambres', () => {
    it('should call sendRequest with /chambres-liste/services/{serviceId}', () => {
      simulateGetChambres()
      const { getChambres } = useChambresList()

      getChambres(42)

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/chambres-liste/services/42' },
        expect.any(Function)
      )
    })

    it('should populate list with data returned from API', async () => {
      simulateGetChambres()
      const { getChambres, list } = useChambresList()

      getChambres(1)
      await new Promise((r) => setTimeout(r, 0))

      expect(list.value).toEqual(mockServiceResponse)
    })

    it('should populate suggestions from the services store', async () => {
      simulateGetChambres()
      const { suggestions } = useChambresList()

      await new Promise((r) => setTimeout(r, 0))

      expect(suggestions.value).toEqual(
        mockServicesList.value.map((s) => s.nom)
      )
    })
  })

  // --- search: filters suggestions from store, filters list locally ---
  describe('search (case-insensitive prefix filtering)', () => {
    it('should filter suggestions from store by case-insensitive prefix', () => {
      simulateGetChambres()
      const { search, suggestions } = useChambresList()

      search({ query: 'car' } as any)

      expect(suggestions.value).toEqual(['Cardiologie', 'cardiologie pédiatrique'])
    })

    it('should filter list by case-insensitive prefix', () => {
      const multiResponse = [
        { id_service: 1, nom: 'Cardiologie', chambres: [] },
        { id_service: 3, nom: 'cardiologie pédiatrique', chambres: [] }
      ]
      simulateGetChambres(multiResponse)
      const { getChambres, search, list } = useChambresList()

      // Populate list with multiple services
      getChambres(1)
      search({ query: 'Car' } as any)

      expect(list.value).toEqual([
        { id_service: 1, nom: 'Cardiologie', chambres: [] },
        { id_service: 3, nom: 'cardiologie pédiatrique', chambres: [] }
      ])
    })

    it('should keep current list when query does not match any loaded service', () => {
      simulateGetChambres()
      const { getChambres, search, list } = useChambresList()

      getChambres(1)
      const listBefore = [...list.value]
      search({ query: 'zzz_no_match' } as any)

      // No match → list stays unchanged
      expect(list.value).toEqual(listBefore)
    })

    it('should set suggestions to empty when query does not match any store service', () => {
      simulateGetChambres()
      const { search, suggestions } = useChambresList()

      search({ query: 'zzz_no_match' } as any)

      expect(suggestions.value).toEqual([])
    })
  })

  // --- searchBySelect: calls getChambres with the matching serviceId ---
  describe('searchBySelect', () => {
    it('should update searchValue with the selected value', () => {
      simulateGetChambres()
      const { searchBySelect, searchValue } = useChambresList()

      searchBySelect({ value: 'Cardiologie' } as any)

      expect(searchValue.value).toBe('Cardiologie')
    })

    it('should call getChambres with the matching service id from store', () => {
      simulateGetChambres()
      const { searchBySelect } = useChambresList()

      mockSendRequest.mockClear()
      searchBySelect({ value: 'Chirurgie' } as any)

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/chambres-liste/services/2' },
        expect.any(Function)
      )
    })

    it('should not call getChambres if service name not found in store', () => {
      simulateGetChambres()
      const { searchBySelect } = useChambresList()

      mockSendRequest.mockClear()
      searchBySelect({ value: 'ServiceInexistant' } as any)

      expect(mockSendRequest).not.toHaveBeenCalled()
    })
  })

  // --- resetSearchValue ---
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

  // --- Reset when searchValue is emptied ---
  describe('reset when searchValue is emptied', () => {
    it('should call getChambres with first store service when searchValue becomes empty', async () => {
      simulateGetChambres()
      const { searchBySelect, searchValue } = useChambresList()

      searchBySelect({ value: 'Chirurgie' } as any)
      searchValue.value = ''

      // Wait multiple ticks for the Vue watcher to flush
      await new Promise((r) => setTimeout(r, 50))

      // The watcher calls getChambres(servicesList[0].id_service) which is 1
      const paths = mockSendRequest.mock.calls.map((c: any[]) => c[0].path)
      expect(paths).toContain('/chambres-liste/services/1')
    })
  })
})

// --- Property-based tests ---
import fc from 'fast-check'

const arbStoreServices = fc.array(
  fc.record({
    id_service: fc.integer({ min: 1, max: 1000 }),
    nom: fc.string({ minLength: 1, maxLength: 30 })
  }),
  { minLength: 1, maxLength: 20 }
)

describe('UseChambresList — Property-based tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockError.value = null
    mockSendRequest.mockReset()
  })

  // **Validates: Requirements 3.2**
  it('search: suggestions should contain only store services whose name starts with the query (case-insensitive)', () => {
    fc.assert(
      fc.property(
        arbStoreServices,
        fc.string({ minLength: 1, maxLength: 10 }),
        (storeServices, query) => {
          // Set up the store with generated services
          mockServicesList.value = storeServices
          simulateGetChambres([])
          const { search, suggestions } = useChambresList()

          search({ query } as any)

          const expected = storeServices
            .filter((s) => s.nom.toLowerCase().startsWith(query.toLowerCase()))
            .map((s) => s.nom)

          expect(suggestions.value).toEqual(expected)
        }
      ),
      { numRuns: 100 }
    )
  })

  // **Validates: Requirements 3.4**
  it('searchBySelect: should call getChambres with the correct serviceId when name matches', () => {
    fc.assert(
      fc.property(
        arbStoreServices,
        (storeServices) => {
          if (storeServices.length === 0) return

          mockServicesList.value = storeServices
          simulateGetChambres([])
          const { searchBySelect } = useChambresList()

          // Pick a random service from the store
          const target = storeServices[0]
          mockSendRequest.mockClear()
          simulateGetChambres([])
          searchBySelect({ value: target.nom } as any)

          // Should have called with the matching service id
          const matchingService = storeServices.find((s) => s.nom === target.nom)
          if (matchingService) {
            expect(mockSendRequest).toHaveBeenCalledWith(
              { path: `/chambres-liste/services/${matchingService.id_service}` },
              expect.any(Function)
            )
          }
        }
      ),
      { numRuns: 100 }
    )
  })
})
