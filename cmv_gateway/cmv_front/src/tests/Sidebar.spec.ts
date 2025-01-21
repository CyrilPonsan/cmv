// Import des dépendances nécessaires pour les tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory } from 'vue-router'
import SidebarComponent from '@/components/navigation/sidebar/SidebarComponent.vue'
import { useUserStore } from '@/stores/user'

// Mock des composants enfants
vi.mock('@/components/navigation/sidebar/SidebarAccueil.vue', () => ({
  default: {
    name: 'SidebarAccueil',
    template: '<div class="sidebar-accueil"></div>'
  }
}))

vi.mock('@/components/navigation/sidebar/SidebarFooter.vue', () => ({
  default: {
    name: 'SidebarFooter',
    template: '<div class="sidebar-footer"></div>'
  }
}))

// Configuration du router pour les tests
const router = createRouter({
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

describe('SidebarComponent', () => {
  let wrapper: VueWrapper<InstanceType<typeof SidebarComponent>>
  let userStore: any

  // Configuration initiale avant chaque test
  beforeEach(() => {
    wrapper = mount(SidebarComponent, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              user: { role: '', mode: 'light' }
            }
          }),
          router // Ajout du router aux plugins
        ]
      }
    })
    userStore = useUserStore()
  })

  // Vérifie le rendu de base du composant
  it('renders correctly', () => {
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.find('img').exists()).toBe(true)
  })

  // Vérifie que le logo est présent avec les bons attributs
  it('displays logo correctly', () => {
    const logo = wrapper.find('img')
    expect(logo.attributes('src')).toContain('cmv-logo.jpeg')
    expect(logo.attributes('alt')).toBe('logo')
  })

  // Vérifie que SidebarAccueil est masqué par défaut (role non défini)
  it('hides SidebarAccueil when role is not home', () => {
    expect(wrapper.find('.sidebar-accueil').exists()).toBe(false)
  })

  // Vérifie que SidebarAccueil est affiché quand le rôle est 'home'
  it('shows SidebarAccueil when role is home', async () => {
    await userStore.$patch({ role: 'home' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.sidebar-accueil').exists()).toBe(true)
  })

  // Vérifie que SidebarFooter est toujours présent
  it('always displays SidebarFooter', () => {
    expect(wrapper.find('.sidebar-footer').exists()).toBe(true)
  })

  // Vérifie les classes CSS principales
  it('has correct CSS classes', () => {
    const main = wrapper.find('main')
    expect(main.classes()).toContain('w-64')
    expect(main.classes()).toContain('sticky')
    expect(main.classes()).toContain('bg-surface-900')
  })
})
