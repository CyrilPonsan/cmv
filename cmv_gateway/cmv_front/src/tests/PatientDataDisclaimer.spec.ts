import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import PatientDataDisclaimer from '@/components/create-update-patient/PatientDataDisclaimer.vue'

// Mock des traductions
const messages = {
  fr: {
    components: {
      patient_data_disclaimer: {
        title: 'Titre test',
        legal_context_title: 'Contexte légal',
        legal_context_text: 'Texte contexte légal',
        principle_1: 'Principe 1',
        principle_2: 'Principe 2',
        principle_3: 'Principe 3',
        principle_4: 'Principe 4',
        responsibilities_title: 'Responsabilités',
        responsibilities_text: 'Texte responsabilités',
        responsibility_1: 'Responsabilité 1',
        responsibility_2: 'Responsabilité 2',
        responsibility_3: 'Responsabilité 3',
        responsibility_4: 'Responsabilité 4'
      }
    }
  }
}

// Configuration i18n pour les tests
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages
})

describe('PatientDataDisclaimer', () => {
  const wrapper = mount(PatientDataDisclaimer, {
    global: {
      plugins: [i18n]
    }
  })

  it('devrait monter le composant correctement', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('devrait afficher le titre principal', () => {
    const title = wrapper.find('h3')
    expect(title.text()).toBe('Titre test')
  })

  it('devrait afficher la section du contexte légal', () => {
    const legalContext = wrapper.find('h4')
    expect(legalContext.text()).toBe('Contexte légal')

    const principles = wrapper.findAll('ul li')
    expect(principles).toHaveLength(4)
    expect(principles[0].text()).toContain('Principe 1')
  })

  it('devrait afficher la section des responsabilités', () => {
    const responsibilities = wrapper.findAll('ol li')
    expect(responsibilities).toHaveLength(4)
    expect(responsibilities[0].text()).toContain('Responsabilité 1')
  })

  it('devrait avoir les classes CSS appropriées', () => {
    const mainTitle = wrapper.find('h3')
    expect(mainTitle.classes()).toContain('text-primary-500')
    expect(mainTitle.classes()).toContain('font-bold')

    const sections = wrapper.findAll('.surface-100')
    expect(sections).toHaveLength(2)
    sections.forEach((section) => {
      expect(section.classes()).toContain('p-3')
      expect(section.classes()).toContain('border-round')
    })
  })
})
