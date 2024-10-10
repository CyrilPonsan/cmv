import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createWebHistory, type Router } from 'vue-router'
import App from './App.vue'
import { useUserStore } from './stores/user'
import { createTestingPinia } from '@pinia/testing'

// Mock des composants
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    render: () => null
  }
}))

vi.mock('primevue/toast', () => ({
  default: {
    name: 'Toast',
    render: () => null
  }
}))

// Mock du router
const router: Router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: '<div>Home</div>' } }]
})

describe('App', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>
  let userStore: any

  beforeEach(() => {
    wrapper = mount(App, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn
          }),
          router
        ],
        stubs: ['RouterView']
      }
    })
    userStore = useUserStore()
  })

  it('renders correctly', () => {
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('toggles color scheme when button is clicked', async () => {
    const toggleButton = wrapper.find('button[aria-label="mode d\'affichage"]')
    await toggleButton.trigger('click')
    expect(userStore.toggleColorScheme).toHaveBeenCalledTimes(1)
  })

  it('shows logout button when user is logged in', async () => {
    await userStore.$patch({ role: 'user' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[aria-label="déconnexion"]').exists()).toBe(true)
  })

  it('hides logout button when user is not logged in', async () => {
    await userStore.$patch({ role: '' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[aria-label="déconnexion"]').exists()).toBe(false)
  })

  it('calls handshake on beforeMount', () => {
    expect(userStore.handshake).toHaveBeenCalledTimes(1)
  })

  it('redirects to patients page when role is home', async () => {
    const routerPushSpy = vi.spyOn(router, 'push')
    await userStore.$patch({ role: 'home' })
    await wrapper.vm.$nextTick()
    expect(routerPushSpy).toHaveBeenCalledWith({ name: 'patients' })
  })

  // Ajoutez d'autres tests pour couvrir les différents scénarios de redirection, etc.
})
