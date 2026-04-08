import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

// Mock LoginForm child component
vi.mock('@/components/LoginForm.vue', () => ({
  default: {
    name: 'LoginForm',
    template: '<div data-testid="login-form">LoginForm</div>'
  }
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

// Mock PrimeVue Button used in NotFound
vi.mock('primevue/button', () => ({
  default: {
    name: 'Button',
    props: ['as', 'to', 'label', 'variant'],
    template: '<component :is="as || \'button\'" :to="to">{{ label }}<slot /></component>'
  }
}))

import LoginView from '@/views/LoginView.vue'
import NotFound from '@/views/NotFound.vue'
import NetworkIssue from '@/views/NetworkIssue.vue'

/**
 * Tests des vues simples : LoginView, NotFound, NetworkIssue
 * Validates: Requirements 10.1, 10.2, 10.3
 */
describe('SimpleViews', () => {
  /**
   * LoginView — Validates: Requirement 10.1
   */
  describe('LoginView', () => {
    it('should render the LoginForm component', () => {
      const wrapper = shallowMount(LoginView, {
        global: {
          stubs: {
            'router-link': true
          }
        }
      })

      const loginForm = wrapper.findComponent({ name: 'LoginForm' })
      expect(loginForm.exists()).toBe(true)
    })
  })

  /**
   * NotFound — Validates: Requirement 10.2
   */
  describe('NotFound', () => {
    it('should display the 404 error message', () => {
      const wrapper = shallowMount(NotFound, {
        global: {
          stubs: {
            'router-link': true
          }
        }
      })

      const heading = wrapper.find('h1')
      expect(heading.exists()).toBe(true)
      expect(heading.text()).toContain('404')
      expect(heading.text()).toContain("La page n'existe pas")
    })

    it('should have a link back to home', () => {
      const wrapper = shallowMount(NotFound, {
        global: {
          stubs: {
            'router-link': true
          }
        }
      })

      // Button is rendered with as="router-link" and to="/"
      const button = wrapper.findComponent({ name: 'Button' })
      expect(button.exists()).toBe(true)
      expect(button.props('to')).toBe('/')
      expect(button.props('label')).toBe("Retour à l'accueil")
    })
  })

  /**
   * NetworkIssue — Validates: Requirement 10.3
   */
  describe('NetworkIssue', () => {
    it('should display the server problem message', () => {
      const wrapper = shallowMount(NetworkIssue)

      const heading = wrapper.find('h1')
      expect(heading.exists()).toBe(true)
      expect(heading.text()).toContain('Problème serveur')
    })
  })
})
