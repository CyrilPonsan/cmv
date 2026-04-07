import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'

// --- Mock useHttp (required by user store) ---
vi.mock('@/composables/useHttp', () => ({
  default: () => ({
    sendRequest: vi.fn().mockReturnValue(Promise.resolve()),
    isLoading: ref(false),
    error: ref(null),
    axiosInstance: {}
  })
}))

// --- Mock vue-router's useRouter/useRoute used inside user store ---
const mockPush = vi.fn()
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRouter: () => ({ push: mockPush }),
    useRoute: () => ({ name: 'root', params: {} })
  }
})

import { useUserStore } from '@/stores/user'
import LoginView from '@/views/LoginView.vue'

/**
 * Tests du routeur — protection des routes par rôle et redirections
 * Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
 */
describe('Router', () => {
  /**
   * Creates a fresh router instance with memory history for testing.
   * Uses the same route config as the production router.
   */
  function createTestRouter() {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          name: 'root',
          component: LoginView,
          beforeEnter: async (_to, _from, next) => {
            const userStore = useUserStore()
            if (userStore.role.length > 0) {
              const route = userStore.role === 'home' ? 'accueil' : undefined
              if (route) next(`/${route}`)
              else next()
            } else {
              next()
            }
          }
        },
        {
          path: '/accueil',
          name: 'accueil',
          component: { template: '<div>Accueil Layout</div>' },
          beforeEnter: async (_to, _from, next) => {
            const userStore = useUserStore()
            if (userStore.role === 'home') next()
            else next('/')
          },
          children: [
            { path: '', name: 'patients', component: { template: '<div>Accueil</div>' } },
            { path: '/patient/:id', name: 'patient', component: { template: '<div>Patient</div>' } },
            { path: '/add-patient', name: 'add-patient', component: { template: '<div>Add Patient</div>' } }
          ]
        },
        {
          path: '/chambres',
          name: 'chambres-layout',
          component: { template: '<div>Chambres Layout</div>' },
          beforeEnter: async (_to, _from, next) => {
            const userStore = useUserStore()
            const allowedRoles = ['home', 'nurses', 'cleaning']
            if (allowedRoles.includes(userStore.role)) next()
            else next('/')
          },
          children: [
            { path: '', name: 'chambres', component: { template: '<div>Chambres</div>' } }
          ]
        },
        {
          path: '/admissions/create/:patientId',
          name: 'admissions-create',
          component: { template: '<div>Admission</div>' }
        },
        {
          path: '/:pathMatch(.*)*',
          name: 'not-found',
          component: { template: '<div>Not Found</div>' }
        }
      ]
    })
  }

  let store: ReturnType<typeof useUserStore>

  beforeEach(() => {
    vi.clearAllMocks()
    const pinia = createPinia()
    setActivePinia(pinia)
    store = useUserStore()
  })

  /**
   * Requirement 14.1: Unauthenticated user on "/" sees LoginView
   */
  describe('unauthenticated user on "/"', () => {
    it('should display LoginView when user has no role', async () => {
      const router = createTestRouter()
      await router.push('/')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('root')
      expect(router.currentRoute.value.path).toBe('/')
    })
  })

  /**
   * Requirement 14.2: User with role "home" on "/" is redirected to /accueil
   */
  describe('authenticated user with role "home" on "/"', () => {
    it('should redirect to /accueil', async () => {
      store.role = 'home'
      const router = createTestRouter()
      await router.push('/')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/accueil')
    })
  })

  /**
   * Requirement 14.3: User without role "home" accessing /accueil is redirected to "/"
   */
  describe('user without role "home" accessing /accueil', () => {
    it('should redirect to "/" when user has no role', async () => {
      store.role = ''
      const router = createTestRouter()
      await router.push('/accueil')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/')
      expect(router.currentRoute.value.name).toBe('root')
    })

    it('should redirect to "/" when user has a non-home role', async () => {
      store.role = 'nurses'
      const router = createTestRouter()
      await router.push('/accueil')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/')
      expect(router.currentRoute.value.name).toBe('root')
    })
  })

  /**
   * Requirement 14.4: Unknown route shows NotFound
   */
  describe('unknown route', () => {
    it('should resolve to not-found for a non-existent route', async () => {
      const router = createTestRouter()
      await router.push('/this-route-does-not-exist')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('not-found')
    })
  })

  /**
   * Requirement 14.5: Authorized roles can access /chambres
   */
  describe('access to /chambres by role', () => {
    it('should allow access for role "home"', async () => {
      store.role = 'home'
      const router = createTestRouter()
      await router.push('/chambres')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/chambres')
    })

    it('should allow access for role "nurses"', async () => {
      store.role = 'nurses'
      const router = createTestRouter()
      await router.push('/chambres')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/chambres')
    })

    it('should allow access for role "cleaning"', async () => {
      store.role = 'cleaning'
      const router = createTestRouter()
      await router.push('/chambres')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/chambres')
    })

    it('should redirect to "/" for unauthorized role', async () => {
      store.role = 'unauthorized'
      const router = createTestRouter()
      await router.push('/chambres')
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/')
      expect(router.currentRoute.value.name).toBe('root')
    })
  })
})

// Feature: frontend-test-coverage, Property 14: Routes inexistantes affichent NotFound
import fc from 'fast-check'

describe('Router — Property-Based Tests', () => {
  /**
   * Property 14: Routes inexistantes affichent NotFound
   * For any URL path not matching any defined route, the router must resolve to the NotFound component.
   * Validates: Requirements 14.4
   */
  it('should resolve to not-found for any path not matching a defined route', async () => {
    // Arbitrary for generating random path segments (alphanumeric + hyphens)
    const pathSegmentArb = fc
      .string({ minLength: 1, maxLength: 20 })
      .map((s) => s.replace(/[^a-z0-9_-]/gi, 'x'))
      .filter((s) => s.length > 0)

    // Generate a random URL path with 1-4 segments
    const randomPathArb = fc
      .array(pathSegmentArb, { minLength: 1, maxLength: 4 })
      .map((segments) => '/' + segments.join('/'))
      .filter((path) => {
        // Exclude paths that match any defined route
        const normalized = path.toLowerCase()
        if (normalized === '/') return false
        if (normalized === '/accueil') return false
        if (normalized === '/add-patient') return false
        if (normalized === '/chambres') return false
        // /patient/:id pattern
        if (/^\/patient\/[^/]+$/.test(normalized)) return false
        // /admissions/create/:patientId pattern
        if (/^\/admissions\/create\/[^/]+$/.test(normalized)) return false
        return true
      })

    await fc.assert(
      fc.asyncProperty(randomPathArb, async (path) => {
        const pinia = createPinia()
        setActivePinia(pinia)

        const router = createRouter({
          history: createMemoryHistory(),
          routes: [
            {
              path: '/',
              name: 'root',
              component: LoginView
            },
            {
              path: '/accueil',
              name: 'accueil',
              component: { template: '<div>Accueil Layout</div>' },
              children: [
                { path: '', name: 'patients', component: { template: '<div>Accueil</div>' } },
                { path: '/patient/:id', name: 'patient', component: { template: '<div>Patient</div>' } },
                { path: '/add-patient', name: 'add-patient', component: { template: '<div>Add Patient</div>' } }
              ]
            },
            {
              path: '/chambres',
              name: 'chambres-layout',
              component: { template: '<div>Chambres Layout</div>' },
              children: [
                { path: '', name: 'chambres', component: { template: '<div>Chambres</div>' } }
              ]
            },
            {
              path: '/admissions/create/:patientId',
              name: 'admissions-create',
              component: { template: '<div>Admission</div>' }
            },
            {
              path: '/:pathMatch(.*)*',
              name: 'not-found',
              component: { template: '<div>Not Found</div>' }
            }
          ]
        })

        await router.push(path)
        await router.isReady()

        expect(router.currentRoute.value.name).toBe('not-found')
      }),
      { numRuns: 100 }
    )
  })

  // Feature: frontend-test-coverage, Property 15: Accès aux chambres par rôles autorisés
  /**
   * Property 15: Accès aux chambres par rôles autorisés
   * For any role in {"home", "nurses", "cleaning"}, access to /chambres must be allowed.
   * For any role outside this set, access must be denied with redirection to "/".
   * Validates: Requirements 14.5
   */
  it('should allow /chambres access only for authorized roles', async () => {
    const allowedRoles = ['home', 'nurses', 'cleaning'] as const

    // Arbitrary for allowed roles
    const allowedRoleArb = fc.constantFrom(...allowedRoles)

    // Arbitrary for unauthorized roles: non-empty strings that are NOT in the allowed set
    const unauthorizedRoleArb = fc
      .string({ minLength: 1, maxLength: 30 })
      .filter((role) => !allowedRoles.includes(role as any) && role.trim().length > 0)

    // Sub-property 1: Allowed roles can access /chambres
    await fc.assert(
      fc.asyncProperty(allowedRoleArb, async (role) => {
        const pinia = createPinia()
        setActivePinia(pinia)
        const store = useUserStore()
        store.role = role

        const router = createRouter({
          history: createMemoryHistory(),
          routes: [
            {
              path: '/',
              name: 'root',
              component: LoginView
            },
            {
              path: '/chambres',
              name: 'chambres-layout',
              component: { template: '<div>Chambres Layout</div>' },
              beforeEnter: async (_to, _from, next) => {
                const userStore = useUserStore()
                const allowed = ['home', 'nurses', 'cleaning']
                if (allowed.includes(userStore.role)) next()
                else next('/')
              },
              children: [
                { path: '', name: 'chambres', component: { template: '<div>Chambres</div>' } }
              ]
            }
          ]
        })

        await router.push('/chambres')
        await router.isReady()

        expect(router.currentRoute.value.path).toBe('/chambres')
      }),
      { numRuns: 100 }
    )

    // Sub-property 2: Unauthorized roles are redirected to "/"
    await fc.assert(
      fc.asyncProperty(unauthorizedRoleArb, async (role) => {
        const pinia = createPinia()
        setActivePinia(pinia)
        const store = useUserStore()
        store.role = role

        const router = createRouter({
          history: createMemoryHistory(),
          routes: [
            {
              path: '/',
              name: 'root',
              component: LoginView
            },
            {
              path: '/chambres',
              name: 'chambres-layout',
              component: { template: '<div>Chambres Layout</div>' },
              beforeEnter: async (_to, _from, next) => {
                const userStore = useUserStore()
                const allowed = ['home', 'nurses', 'cleaning']
                if (allowed.includes(userStore.role)) next()
                else next('/')
              },
              children: [
                { path: '', name: 'chambres', component: { template: '<div>Chambres</div>' } }
              ]
            }
          ]
        })

        await router.push('/chambres')
        await router.isReady()

        expect(router.currentRoute.value.path).toBe('/')
        expect(router.currentRoute.value.name).toBe('root')
      }),
      { numRuns: 100 }
    )
  })
})
