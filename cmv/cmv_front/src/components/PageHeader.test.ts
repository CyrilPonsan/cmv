import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageHeader from './PageHeader.vue'

describe('PageHeader', () => {
  it('rend correctement le titre et la description', () => {
    const wrapper = mount(PageHeader, {
      props: {
        title: 'Titre de test',
        description: 'Description de test'
      }
    })

    // Vérifie que le titre est correctement rendu
    expect(wrapper.find('h1').text()).toBe('Titre de test')

    // Vérifie que la description est correctement rendue
    expect(wrapper.find('h2').text()).toBe('Description de test')
  })

  it('applique les classes CSS correctement', () => {
    const wrapper = mount(PageHeader, {
      props: {
        title: 'Titre',
        description: 'Description'
      }
    })

    // Vérifie les classes du titre
    expect(wrapper.find('h1').classes()).toContain('text-3xl')
    expect(wrapper.find('h1').classes()).toContain('font-bold')

    // Vérifie les classes de la description
    expect(wrapper.find('h2').classes()).toContain('text-sm')
    expect(wrapper.find('h2').classes()).toContain('text-neutral-500/50')
    expect(wrapper.find('h2').classes()).toContain('font-bold')
  })
})
