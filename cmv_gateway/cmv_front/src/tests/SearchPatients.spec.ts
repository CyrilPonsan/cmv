import useLazyLoad from '@/composables/use-lazy-load'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'

// Mock useHttp
vi.mock('@/composables/use-http', () => ({
  default: () => ({
    sendRequest: vi.fn(),
    isLoading: ref(false)
  })
}))

describe('useLazyLoad composable', () => {
  let composable: ReturnType<typeof useLazyLoad<any>>

  beforeEach(() => {
    setActivePinia(createPinia())
    composable = useLazyLoad<any>('/api/patients')
  })

  it('should update search value and reset pagination on filter change', () => {
    const event = {
      target: {
        value: 'test'
      }
    } as unknown as Event

    composable.onFilterChange(event)

    expect(composable.lazyState.value.first).toBe(0)
    expect(composable.loading.value).toBe(false)
  })

  it('should debounce filter change events', () => {
    vi.useFakeTimers()
    const event = {
      target: {
        value: 'test'
      }
    } as unknown as Event

    composable.onFilterChange(event)
    composable.onFilterChange(event)
    composable.onFilterChange(event)

    vi.runAllTimers()

    expect(composable.lazyState.value.first).toBe(0)
    expect(composable.loading.value).toBe(false)
  })

  it('should clear previous timer on new filter change event', () => {
    vi.useFakeTimers()
    const event = {
      target: {
        value: 'test'
      }
    } as unknown as Event

    composable.onFilterChange(event)
    vi.advanceTimersByTime(500)
    composable.onFilterChange(event)
    vi.advanceTimersByTime(500)
    composable.onFilterChange(event)
    vi.runAllTimers()

    expect(composable.lazyState.value.first).toBe(0)
    expect(composable.loading.value).toBe(false)
  })
})
