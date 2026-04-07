import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { RouterView } from 'vue-router'

import AccueilLayout from '@/views/AccueilLayout.vue'
import ChambresLayout from '@/views/ChambresLayout.vue'

/**
 * Tests des vues layout : AccueilLayout, ChambresLayout
 * Validates: Requirements 11.1, 11.2
 */
describe('LayoutViews', () => {
  /**
   * AccueilLayout — Validates: Requirement 11.1
   */
  describe('AccueilLayout', () => {
    it('should contain a RouterView component', () => {
      const wrapper = shallowMount(AccueilLayout, {
        global: {
          stubs: {
            RouterView: true
          }
        }
      })

      const routerView = wrapper.findComponent(RouterView)
      expect(routerView.exists()).toBe(true)
    })
  })

  /**
   * ChambresLayout — Validates: Requirement 11.2
   */
  describe('ChambresLayout', () => {
    it('should contain a RouterView component', () => {
      const wrapper = shallowMount(ChambresLayout, {
        global: {
          stubs: {
            RouterView: true
          }
        }
      })

      const routerView = wrapper.findComponent(RouterView)
      expect(routerView.exists()).toBe(true)
    })
  })
})
