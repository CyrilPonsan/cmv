import { describe, it, expect, vi, beforeEach } from 'vitest'
import { config, mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory, type Router } from 'vue-router'
import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'
import en from './locales/en.json'
import App from './App.vue'
import { useUserStore } from './stores/user'

const i18n = createI18n({
  legacy: false, // Composition API
  locale: 'fr',
  fallbackLocale: 'fr',
  messages: {
    fr,
    en
  }
})

config.global.plugins = [...(config.global.plugins || []), i18n]

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

describe('App', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>
  let userStore: any

  // Fonction utilitaire pour créer l'instance i18n avec la locale spécifiée
  const createI18nInstance = (locale: 'fr' | 'en') => {
    return createI18n({
      legacy: false,
      locale,
      fallbackLocale: 'en',
      messages: {
        fr,
        en
      }
    })
  }

  beforeEach(() => {
    wrapper = mount(App, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              user: { role: '', mode: 'light' }
            }
          }),
          router
        ],
        stubs: ['RouterView']
      }
    })
    userStore = useUserStore()
  })

  it('displays footer in French when locale is fr', () => {
    const footer = wrapper.find('footer')
    expect(footer.text()).toBe(fr.app.footer)
  })

  it('displays footer in English when locale is en', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(App, {
      global: {
        plugins: [i18n]
      }
    })

    const footer = wrapper.find('footer h3')
    expect(footer.text()).toBe(en.app.footer)
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
