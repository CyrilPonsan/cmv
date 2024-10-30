import { beforeEach, describe, expect, it, vi } from 'vitest'
import { config, mount } from '@vue/test-utils'
import ListPatients from '@/components/ListPatients.vue'
import { createI18n } from 'vue-i18n'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

const i18n = createI18n({
  legacy: false, // Composition API
  locale: 'fr',
  datetimeFormats: {
    fr: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    },
    en: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    }
  },
  fallbackLocale: 'fr',
  messages: {
    fr,
    en
  }
})

config.global.plugins = [...(config.global.plugins || []), i18n]

// Données de test
const mockPatientsList = [
  {
    id_patient: 1,
    nom: 'Dupont',
    prenom: 'Jean',
    email: 'jean.dupont@email.com',
    date_de_naissance: '1990-01-01'
  },
  {
    id_patient: 2,
    nom: 'Martin',
    prenom: 'Marie',
    email: 'marie.martin@email.com',
    date_de_naissance: '1985-05-15'
  }
]

// Mock des dépendances
vi.mock('primevue/usetoast', () => ({
  useToast: () => ({
    add: vi.fn()
  })
}))

// Mock du composable useLazyLoad
vi.mock('@/composables/use-lazy-load', () => ({
  default: () => ({
    getData: vi.fn(),
    lazyState: {
      first: 0,
      rows: 10,
      sortField: null,
      sortOrder: null
    },
    loading: false,
    onLazyLoad: vi.fn(),
    onSort: vi.fn(),
    result: mockPatientsList,
    totalRecords: 2
  })
}))

describe('ListPatients', () => {
  let wrapper: any

  beforeEach(() => {
    // Création des stubs avec les données
    const DataTableStub = {
      template: `
        <div class="p-datatable">
          <div class="p-paginator">
            <slot name="paginatorstart"></slot>
          </div>
          <div class="p-datatable-wrapper">
            <slot></slot>
          </div>
        </div>
      `,
      props: ['value', 'lazy', 'loading', 'totalRecords', 'rows']
    }

    const ColumnStub = {
      template: `
        <div class="p-column">
          <div class="p-column-header">{{ header }}</div>
          <div class="p-column-body">
            <slot name="body" v-bind="{ data: props.value?.[0] || {} }"></slot>
          </div>
        </div>
      `,
      props: ['field', 'header', 'sortable', 'value'],
      setup(props: any) {
        return {
          props
        }
      }
    }

    wrapper = mount(ListPatients, {
      global: {
        stubs: {
          DataTable: DataTableStub,
          Column: ColumnStub
        },
        mocks: {
          d: (date: Date) => date.toLocaleDateString()
        }
      },
      props: {
        // Si votre composant attend des props, les ajouter ici
      },
      data() {
        return {
          patientsList: mockPatientsList
        }
      }
    })
  })

  it('monte correctement le composant', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('affiche les colonnes correctement', () => {
    const columns = wrapper.findAll('.p-column-header')
    expect(columns.length).toBeGreaterThan(0)
    expect(columns[0].text()).toBe(fr.columns.patientsList.civilite)
    expect(columns[columns.length - 2].text()).toBe(fr.columns.patientsList.email)
  })

  it('affiche le nombre total de patients', () => {
    const paginator = wrapper.find('.p-paginator')
    expect(paginator.exists()).toBe(true)
    expect(paginator.text()).toContain('2 patients')
  })

  it("affiche l'icône de suppression", () => {
    const lastColumn = wrapper.findAll('.p-column').at(-1)
    expect(lastColumn.exists()).toBe(true)
    const trashIcon = lastColumn.find('.pi-trash')
    expect(trashIcon.exists()).toBe(true)
  })

  it("déclenche le toast lors du clic sur l'icône de suppression", async () => {
    const lastColumn = wrapper.findAll('.p-column').at(-1)
    const trashIcon = lastColumn.find('.pi-trash')
    await trashIcon.trigger('click')
    // Ici vous pouvez ajouter la vérification que le toast a été appelé
  })
})
