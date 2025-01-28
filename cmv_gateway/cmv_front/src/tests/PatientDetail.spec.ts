import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PatientDetail from '@/components/PatientDetail.vue'
import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'

// Mock du composant Panel de PrimeVue
vi.mock('primevue/panel', () => ({
  default: {
    name: 'Panel',
    template:
      '<div class="p-panel"><div class="p-panel-header">{{ header }}</div><div class="p-panel-content"><slot /></div></div>',
    props: ['header']
  }
}))

// Configuration i18n pour les tests
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: { fr },
  datetimeFormats: {
    fr: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    }
  }
})

describe('PatientDetail', () => {
  const mockPatient = {
    id_patient: 1,
    civilite: 'M.',
    nom: 'Dupont',
    prenom: 'Jean',
    email: 'jean.dupont@email.com',
    telephone: '0123456789',
    date_de_naissance: '1990-01-01',
    adresse: '1 rue de la Paix',
    code_postal: '75000',
    ville: 'Paris',
    documents: [],
    latest_admission: {
      id_admission: 1,
      entree_le: 'date',
      ambulatoire: true,
      sorti_le: null,
      sortie_prevue_le: '2024-01-20',
      ref_chambre: '1',
      nom_chambre: 'Chambre 101'
    }
  }

  const mountComponent = () => {
    return mount(PatientDetail, {
      props: {
        detailPatient: mockPatient
      },
      global: {
        plugins: [i18n]
      }
    })
  }

  it('affiche correctement le nom complet du patient', () => {
    const wrapper = mountComponent()
    const fullName = wrapper.find('.p-panel-content p')
    expect(fullName.text()).toBe('M. Jean Dupont')
  })

  it('masque la civilité si elle est "autre"', () => {
    const patientAutre = {
      ...mockPatient,
      civilite: 'autre'
    }
    const wrapper = mount(PatientDetail, {
      props: {
        detailPatient: patientAutre
      },
      global: {
        plugins: [i18n]
      }
    })
    const fullName = wrapper.find('.p-panel-content p')
    expect(fullName.text().trim()).toBe('Jean Dupont')
  })

  it('affiche correctement la date de naissance formatée', () => {
    const wrapper = mountComponent()
    const panels = wrapper.findAll('.p-panel')
    const birthDatePanel = panels[1]
    expect(birthDatePanel.text()).toContain('01/01/1990')
  })

  it("affiche correctement l'adresse complète", () => {
    const wrapper = mountComponent()
    const panels = wrapper.findAll('.p-panel')
    const addressPanel = panels[2]
    const addressLines = addressPanel.findAll('p')

    expect(addressLines[0].text()).toBe(mockPatient.adresse)
    expect(addressLines[1].text()).toBe(`${mockPatient.code_postal} ${mockPatient.ville}`)
  })

  it('affiche correctement les informations de contact', () => {
    const wrapper = mountComponent()
    const panels = wrapper.findAll('.p-panel')
    const contactPanel = panels[3]
    const contactInfo = contactPanel.findAll('.flex')

    expect(contactInfo[0].text()).toContain(mockPatient.telephone)
    expect(contactInfo[1].text()).toContain(mockPatient.email)
  })

  it('affiche "non renseigné" si l\'email est null', () => {
    const patientSansEmail = {
      ...mockPatient,
      email: null
    }
    const wrapper = mount(PatientDetail, {
      props: {
        detailPatient: {
          ...patientSansEmail,
          email: undefined
        }
      },
      global: {
        plugins: [i18n]
      }
    })
    const panels = wrapper.findAll('.p-panel')
    const contactPanel = panels[3]
    const emailInfo = contactPanel.findAll('.flex')[1]

    expect(emailInfo.text()).toContain(fr.patients.detail.panel.not_provided)
  })
})
