import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

// Mock AdmissionItem
vi.mock('@/components/AdmissionItem.vue', () => ({
  default: {
    name: 'AdmissionItem',
    props: ['admission'],
    template: '<div data-testid="admission-item">AdmissionItem</div>'
  }
}))

// Mock PrimeVue Button
vi.mock('primevue', () => ({
  Button: {
    name: 'Button',
    props: ['label', 'icon', 'variant', 'disabled', 'as', 'to'],
    template: '<button :disabled="disabled" :data-to="to">{{ label }}</button>'
  }
}))

import LatestAdmission from '@/components/LatestAdmission.vue'
import type Admission from '@/models/admission'

const fakeAdmission: Admission = {
  id_admission: 1,
  entree_le: '2026-01-01',
  ambulatoire: false,
  sorti_le: null,
  sortie_prevue_le: '2026-01-05',
  ref_chambre: 'CH01',
  nom_chambre: 'Chambre 101',
  ref_reservation: 42
}

describe('LatestAdmission', () => {
  it('affiche le bouton actif (router-link) quand aucune admission', () => {
    const wrapper = shallowMount(LatestAdmission, {
      props: { latestAdmission: null, patientId: 10 }
    })

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    // Le bouton actif (v-show=true quand null) doit être visible
    const activeBtn = buttons.find(b => b.props('as') === 'router-link')
    expect(activeBtn).toBeDefined()
    expect(activeBtn!.props('to')).toBe('/admissions/create/10')
    expect(activeBtn!.props('disabled')).toBeFalsy()
  })

  it('affiche le bouton disabled quand une admission existe', () => {
    const wrapper = shallowMount(LatestAdmission, {
      props: { latestAdmission: fakeAdmission, patientId: 10 }
    })

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    const disabledBtn = buttons.find(b => b.props('disabled') === true)
    expect(disabledBtn).toBeDefined()
    expect(disabledBtn!.props('label')).toBe('Créer une admission')
  })

  it('affiche AdmissionItem quand une admission existe', () => {
    const wrapper = shallowMount(LatestAdmission, {
      props: { latestAdmission: fakeAdmission, patientId: 10 }
    })

    const item = wrapper.findComponent({ name: 'AdmissionItem' })
    expect(item.exists()).toBe(true)
    expect(item.props('admission')).toEqual(fakeAdmission)
  })

  it('affiche le message "Aucune admission" quand pas d\'admission', () => {
    const wrapper = shallowMount(LatestAdmission, {
      props: { latestAdmission: null, patientId: 10 }
    })

    expect(wrapper.text()).toContain('Aucune admission trouvée')
    expect(wrapper.findComponent({ name: 'AdmissionItem' }).exists()).toBe(false)
  })
})
