// Import des dépendances nécessaires pour les tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory, type Router } from 'vue-router'
import App from '../App.vue'
import { useUserStore } from '../stores/user'
import fr from '../locales/fr.json'
import en from '../locales/en.json'
import { createI18n } from 'vue-i18n'
import PrimeVue from 'primevue/config'

// Mock du composant Button de PrimeVue
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    template: '<button><slot /></button>'
  }
}))

// Mock du composant Toast de PrimeVue
vi.mock('primevue/toast', () => ({
  default: {
    name: 'Toast',
    template: '<div></div>'
  }
}))

// Configuration du router pour les tests avec des routes mockées
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

// Mock de la directive tooltip de PrimeVue
const tooltip = {
  mounted: () => {},
  unmounted: () => {}
}

// Mock du service Toast avec une fonction add espionnée
const toastMock = {
  add: vi.fn()
}

// Mock du hook useToast de PrimeVue
vi.mock('primevue/usetoast', () => ({
  useToast: () => toastMock
}))

/**
 * Fonction utilitaire pour monter le composant App avec les configurations nécessaires
 * @param locale - La locale à utiliser ('fr' ou 'en')
 * @returns Un objet contenant le wrapper du composant monté
 */
const mountComponent = (locale = 'fr') => {
  // Configuration de vue-i18n avec les traductions
  const i18n = createI18n({
    legacy: false,
    locale: locale,
    fallbackLocale: 'fr',
    messages: {
      fr: {
        app: {
          footer: fr.app.footer,
          tooltip: {
            home: 'Accueil',
            change_mode: 'Changer de mode',
            logout: 'Déconnexion'
          }
        }
      },
      en: {
        app: {
          footer: en.app.footer,
          tooltip: {
            home: 'Home',
            change_mode: 'Change mode',
            logout: 'Logout'
          }
        }
      }
    }
  })

  // Montage du composant avec toutes les dépendances nécessaires
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
          router,
          [PrimeVue, { ripple: true }]
        ],
        stubs: {
          RouterView: true,
          Toast: true
        },
        directives: {
          tooltip
        },
        mocks: {
          useToast: () => toastMock
        }
      }
    })
  }
}

// Suite de tests pour la version française de l'application
describe('App tests fr', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>
  let userStore: any

  // Configuration initiale avant chaque test
  beforeEach(() => {
    const mounted = mountComponent('fr')
    wrapper = mounted.wrapper
    userStore = useUserStore()
  })

  // Vérifie que le footer est affiché en français
  it('displays footer in French when locale is fr', () => {
    const footer = wrapper.find('footer')
    expect(footer.text()).toBe(fr.app.footer)
  })

  // Vérifie le rendu des éléments principaux
  it('renders correctly', () => {
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  // Teste le changement de thème
  it('toggles color scheme when button is clicked', async () => {
    const toggleButton = wrapper.find('button[aria-label="theme"]')
    expect(toggleButton.exists()).toBe(true)
    await toggleButton.trigger('click')
    expect(userStore.toggleColorScheme).toHaveBeenCalledTimes(1)
  })

  // Vérifie l'affichage du bouton de déconnexion quand l'utilisateur est connecté
  it('shows logout button when user is logged in', async () => {
    await userStore.$patch({ role: 'user' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[aria-label="déconnexion"]').exists()).toBe(true)
  })

  // Vérifie que le bouton de déconnexion est masqué quand l'utilisateur n'est pas connecté
  it('hides logout button when user is not logged in', async () => {
    await userStore.$patch({ role: '' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[aria-label="déconnexion"]').exists()).toBe(false)
  })

  // Vérifie que la fonction handshake est appelée au montage
  it('calls handshake on beforeMount', () => {
    expect(userStore.handshake).toHaveBeenCalledTimes(1)
  })

  // Vérifie la redirection vers la page patients pour le rôle 'home'
  it('redirects to patients page when role is home', async () => {
    const routerPushSpy = vi.spyOn(router, 'push')
    await userStore.$patch({ role: 'home' })
    await wrapper.vm.$nextTick()
    expect(routerPushSpy).toHaveBeenCalledWith({ name: 'patients' })
  })
})

// Suite de tests pour la version anglaise de l'application
describe('App test en', () => {
  let wrapper: VueWrapper<InstanceType<typeof App>>

  // Configuration initiale avant chaque test
  beforeEach(() => {
    const mounted = mountComponent('en')
    wrapper = mounted.wrapper
  })

  // Vérifie que le footer est affiché en anglais
  it('displays footer in english when locale is en', () => {
    const footer = wrapper.find('footer')
    expect(footer.text()).toBe(en.app.footer)
  })
})
