import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory, type Router } from 'vue-router'
import App from '../App.vue'
import { useUserStore } from '../stores/user'
import { createI18nInstance } from '@/helpers/createI18nInstance'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

// Mock des composants
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button><slot /></button>'
  }
}))

vi.mock('primevue/toast', () => ({
  default: {
    name: 'Toast',
    template: '<div></div>'
  }
}))

// Mock du router
const router: Router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: { template: '<div>Home</div>' }
    },
    {
      path: '/accueil',
      children: [
        {
          path: '',
          name: 'patients',
          component: { template: '<div>Patients</div>' }
        }
      ]
    }
  ]
})

const mountComponent = (locale = 'fr') => {
  const i18n = createI18nInstance(locale)
  return {
    wrapper: mount(App, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              user: { role: '', mode: 'light' }
            }
          }),
          i18n,
          router
        ],
        stubs: ['RouterView'],
        mocks: {
          t: (key: string) => key // Add this mock for t function
        }
      }
    })
  }
}

describe('App tests fr', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>
  let userStore: any

  beforeEach(() => {
    const mounted = mountComponent('fr')
    wrapper = mounted.wrapper
    userStore = useUserStore()
  })

  it('displays footer in French when locale is fr', () => {
    const footer = wrapper.find('footer')
    expect(footer.text()).toBe(fr.app.footer)
  })

  it('renders correctly', () => {
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('toggles color scheme when button is clicked', async () => {
    const toggleButton = wrapper.find('button[aria-label="theme"]')
    expect(toggleButton.exists()).toBe(true)
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
})

describe('App test en', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>

  beforeEach(() => {
    const mounted = mountComponent('en')
    wrapper = mounted.wrapper
  })

  it('displays footer in english when locale is en', () => {
    const footer = wrapper.find('footer')
    expect(footer.text()).toBe(en.app.footer)
  })
})
