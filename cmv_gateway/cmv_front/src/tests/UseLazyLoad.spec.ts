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

// --- Mock onUnmounted (no-op in test) ---
vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onUnmounted: vi.fn()
  }
})

import useLazyLoad from '@/composables/useLazyLoad'

describe('UseLazyLoad', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.restoreAllMocks()
    mockError.value = null
    mockSendRequest.mockReset()
  })

  // --- Requirement 2.1: Default values of lazyState ---
  describe('default lazyState values', () => {
    it('should initialize lazyState with correct defaults', () => {
      const { lazyState } = useLazyLoad('/test')

      expect(lazyState.value).toEqual({
        first: 0,
        rows: 10,
        sortField: 'nom',
        sortOrder: 1
      })
    })

    it('should initialize search as empty string', () => {
      const { search } = useLazyLoad('/test')
      expect(search.value).toBe('')
    })

    it('should initialize totalRecords as 0', () => {
      const { totalRecords } = useLazyLoad('/test')
      expect(totalRecords.value).toBe(0)
    })
  })

  // --- Requirement 2.2: Updating lazyState via onLazyLoad ---
  describe('onLazyLoad updates lazyState', () => {
    it('should update lazyState with pagination event values', async () => {
      const { lazyState, onLazyLoad } = useLazyLoad('/test')

      onLazyLoad({ first: 20, rows: 5, sortField: 'prenom', sortOrder: -1 })

      expect(lazyState.value).toEqual({
        first: 20,
        rows: 5,
        sortField: 'prenom',
        sortOrder: -1
      })
    })

    it('should default sortField to "nom" when event sortField is null', async () => {
      const { lazyState, onLazyLoad } = useLazyLoad('/test')

      onLazyLoad({ first: 10, rows: 10, sortField: null as any, sortOrder: 1 })

      expect(lazyState.value.sortField).toBe('nom')
    })
  })

  // --- Requirement 2.3: Resetting first to 0 on onSort ---
  describe('onSort resets first to 0', () => {
    it('should reset first to 0 when onSort is called', async () => {
      const { lazyState, onLazyLoad, onSort } = useLazyLoad('/test')

      // First, move to a different page
      onLazyLoad({ first: 30, rows: 10, sortField: 'nom', sortOrder: 1 })
      expect(lazyState.value.first).toBe(30)

      // Then sort — first should reset to 0
      onSort({ first: 30, rows: 10, sortField: 'prenom', sortOrder: -1 })
      expect(lazyState.value.first).toBe(0)
    })

    it('should preserve other lazyState properties on sort', async () => {
      const { lazyState, onSort } = useLazyLoad('/test')

      onSort({ first: 10, rows: 10, sortField: 'nom', sortOrder: -1 })

      expect(lazyState.value.rows).toBe(10)
      expect(lazyState.value.sortField).toBe('nom')
      expect(lazyState.value.sortOrder).toBe(1) // onSort spreads existing state, doesn't use event fields
    })
  })

  // --- Requirement 2.4: 300ms debounce on search ---
  describe('search debounce', () => {
    it('should debounce search requests by 300ms', async () => {
      vi.useFakeTimers()

      const { search } = useLazyLoad('/test')

      // Clear any initial getData calls from the watcher
      await Promise.resolve()
      mockSendRequest.mockClear()

      search.value = 'test'

      // Flush the Vue watcher microtask
      await Promise.resolve()
      await Promise.resolve()

      // Before 300ms, searchData should not have been called
      vi.advanceTimersByTime(200)
      await Promise.resolve()
      const callsBeforeDebounce = mockSendRequest.mock.calls.filter((call: any[]) =>
        call[0]?.path?.includes('search=')
      )
      expect(callsBeforeDebounce.length).toBe(0)

      // After 300ms total, the debounced search should fire
      vi.advanceTimersByTime(100)
      await Promise.resolve()
      await Promise.resolve()
      const callsAfterDebounce = mockSendRequest.mock.calls.filter((call: any[]) =>
        call[0]?.path?.includes('search=')
      )
      expect(callsAfterDebounce.length).toBe(1)

      vi.useRealTimers()
    })
  })

  // --- Requirement 2.5: Resetting search via onResetFilter ---
  describe('onResetFilter resets search', () => {
    it('should reset search to empty string', () => {
      const { search, onResetFilter } = useLazyLoad('/test')

      search.value = 'some filter'
      onResetFilter()

      expect(search.value).toBe('')
    })
  })

  // --- Requirement 2.6: Correct HTTP parameter construction in getData ---
  describe('getData constructs correct HTTP parameters', () => {
    it('should call sendRequest with correct URL parameters for default state', async () => {
      vi.useFakeTimers()

      const { getData } = useLazyLoad('/patients')

      mockSendRequest.mockClear()
      getData()

      // Default: page=1 (first=0, rows=10 → 0/10+1=1), limit=10, field=nom, order=asc
      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients?page=1&limit=10&field=nom&order=asc' },
        expect.any(Function)
      )

      vi.useRealTimers()
    })

    it('should compute page correctly from first and rows', async () => {
      vi.useFakeTimers()

      const { onLazyLoad, getData } = useLazyLoad('/patients')

      // Move to page 3: first=20, rows=10 → page = 20/10 + 1 = 3
      onLazyLoad({ first: 20, rows: 10, sortField: 'nom', sortOrder: 1 })

      mockSendRequest.mockClear()
      getData()

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients?page=3&limit=10&field=nom&order=asc' },
        expect.any(Function)
      )

      vi.useRealTimers()
    })

    it('should use "desc" when sortOrder is -1', async () => {
      vi.useFakeTimers()

      const { onLazyLoad, getData } = useLazyLoad('/patients')

      onLazyLoad({ first: 0, rows: 10, sortField: 'prenom', sortOrder: -1 })

      mockSendRequest.mockClear()
      getData()

      expect(mockSendRequest).toHaveBeenCalledWith(
        { path: '/patients?page=1&limit=10&field=prenom&order=desc' },
        expect.any(Function)
      )

      vi.useRealTimers()
    })

    it('should populate result and totalRecords when applyData callback is invoked', async () => {
      vi.useFakeTimers()

      mockSendRequest.mockImplementation((req: any, applyData: (data: any) => void) => {
        applyData({ data: [{ id: 1, nom: 'Dupont' }], total: 42 })
      })

      const { getData, result, totalRecords } = useLazyLoad('/patients')

      getData()

      expect(result.value).toEqual([{ id: 1, nom: 'Dupont' }])
      expect(totalRecords.value).toBe(42)

      vi.useRealTimers()
    })
  })
})

// Feature: frontend-test-coverage, Property 4: Mise à jour de lazyState par pagination
// **Validates: Requirements 2.2**
import fc from 'fast-check'

describe('UseLazyLoad — Property-Based Tests', () => {
  it('Property 4: onLazyLoad updates lazyState.first and lazyState.rows to match event values', () => {
    fc.assert(
      fc.property(
        fc.nat({ max: 10000 }),
        fc.integer({ min: 1, max: 500 }),
        (first, rows) => {
          const { lazyState, onLazyLoad } = useLazyLoad('/test')

          onLazyLoad({ first, rows, sortField: 'nom', sortOrder: 1 })

          expect(lazyState.value.first).toBe(first)
          expect(lazyState.value.rows).toBe(rows)
        }
      ),
      { numRuns: 100 }
    )
  })

  // Feature: frontend-test-coverage, Property 5: Réinitialisation de first lors du tri
  // **Validates: Requirements 2.3**
  it('Property 5: onSort resets lazyState.first to 0 for any non-zero first', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 10000 }),
        fc.integer({ min: 1, max: 500 }),
        fc.constantFrom('nom', 'prenom', 'date_de_naissance'),
        fc.constantFrom(1 as const, -1 as const),
        (first, rows, sortField, sortOrder) => {
          const { lazyState, onLazyLoad, onSort } = useLazyLoad('/test')

          // Set lazyState to a non-zero first via onLazyLoad
          onLazyLoad({ first, rows, sortField, sortOrder })
          expect(lazyState.value.first).toBe(first)

          // Call onSort — first must be reset to 0
          onSort({ first, rows, sortField, sortOrder })
          expect(lazyState.value.first).toBe(0)
        }
      ),
      { numRuns: 100 }
    )
  })

  // Feature: frontend-test-coverage, Property 6: Construction correcte des paramètres URL de getData
  // **Validates: Requirements 2.6**
  it('Property 6: getData constructs URL with correct page, limit, field and order parameters', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 100 }),   // pageIndex (multiplied by rows to get first)
        fc.integer({ min: 1, max: 500 }),    // rows
        fc.constantFrom('nom', 'prenom', 'date_de_naissance', 'email'),
        fc.constantFrom(1 as const, -1 as const),
        (pageIndex, rows, sortField, sortOrder) => {
          const first = pageIndex * rows
          const { onLazyLoad, getData } = useLazyLoad('/test-endpoint')

          // Set lazyState to the generated values
          onLazyLoad({ first, rows, sortField, sortOrder })

          // Clear any calls from the watcher triggered by onLazyLoad
          mockSendRequest.mockClear()

          // Call getData and verify URL construction
          getData()

          const expectedPage = first / rows + 1
          const expectedOrder = sortOrder === 1 ? 'asc' : 'desc'
          const expectedPath = `/test-endpoint?page=${expectedPage}&limit=${rows}&field=${sortField}&order=${expectedOrder}`

          expect(mockSendRequest).toHaveBeenCalledWith(
            { path: expectedPath },
            expect.any(Function)
          )
        }
      ),
      { numRuns: 100 }
    )
  })
})
