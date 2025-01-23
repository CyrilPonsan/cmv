import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListPatients from '@/components/ListPatients.vue'
import { createI18n } from 'vue-i18n'
import PrimeVue from 'primevue/config'
import fr from '../locales/fr.json'
import en from '../locales/en.json'
import { ref } from 'vue'
import { patientsListColumns } from '@/libs/columns/patients-list'

// Configuration i18n
const i18n = createI18n({
  legacy: false,
  locale: 'fr',
  messages: {
    fr: {
      ...fr,
      columns: {
        patientsList: {
          nom: 'Nom',
          prenom: 'Prénom',
          email: 'Email',
          date_de_naissance: 'Date de naissance'
        }
      }
    },
    en
  },
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
  }
})

// Mock des données
const mockPatientsList = [
  {
    id_patient: 1,
    nom: 'Dupont',
    prenom: 'Jean',
    email: 'jean.dupont@email.com',
    date_de_naissance: '1990-01-01',
    telephone: '0123456789'
  },
  {
    id_patient: 2,
    nom: 'Martin',
    prenom: 'Marie',
    email: 'marie.martin@email.com',
    date_de_naissance: '1985-05-15',
    telephone: '0123456789'
  }
]

// Mock du composable useListPatients
vi.mock('@/composables/useListPatients', () => ({
  default: () => ({
    onTrash: vi.fn(),
    handlePage: vi.fn(),
    handleSort: vi.fn(),
    search: ref(''),
    onResetFilter: vi.fn(),
    result: ref(mockPatientsList),
    totalRecords: ref(2),
    lazyState: ref({
      first: 0,
      rows: 10,
      sortField: null,
      sortOrder: null
    }),
    loading: ref(false),
    isLoading: ref(false),
    error: ref(null),
    columns: patientsListColumns
  })
}))

// Mock du toast
const toastMock = {
  add: vi.fn()
}

vi.mock('primevue/usetoast', () => ({
  useToast: () => toastMock
}))

// Mock de la directive tooltip
const tooltip = {
  mounted: () => {},
  unmounted: () => {}
}

// Ajout du mock pour patientsListColumns
vi.mock('@/libs/columns/patients-list', () => ({
  patientsListColumns: [
    { field: 'nom', header: 'nom', sortable: true },
    { field: 'prenom', header: 'prenom', sortable: true },
    { field: 'email', header: 'email', sortable: true },
    { field: 'date_de_naissance', header: 'date_de_naissance', sortable: true },
    { field: 'civilite', header: 'civilite', sortable: false },
    { field: 'telephone', header: 'telephone', sortable: false },
    { field: 'actions', header: 'actions', sortable: false }
  ]
}))

// Déplacer ColumnStub en dehors du beforeEach
const ColumnStub = {
  template: '<th class="p-column"><slot></slot></th>',
  props: ['field', 'header', 'sortable']
}

describe('ListPatients', () => {
  let wrapper: any

  beforeEach(() => {
    // Création des stubs pour les composants PrimeVue
    const DataTableStub = {
      template: `
        <div class="p-datatable">
          <div class="p-paginator">
            <slot name="paginatorstart"></slot>
          </div>
          <table>
            <thead>
              <tr>
                <slot></slot>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in value" :key="item.id_patient">
                <td v-for="col in patientsListColumns" :key="col.field">
                  {{ item[col.field] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      `,
      props: ['value', 'loading', 'totalRecords', 'lazy'],
      data() {
        return {
          patientsListColumns
        }
      }
    }

    wrapper = mount(ListPatients, {
      global: {
        plugins: [i18n, PrimeVue],
        stubs: {
          DataTable: DataTableStub,
          Column: ColumnStub,
          Button: true,
          InputText: true,
          IconField: true,
          InputIcon: true
        },
        directives: {
          tooltip
        }
      }
    })
  })

  it('monte correctement le composant', () => {
    expect(wrapper.exists()).toBe(true)
  })

  console.log({ patientsListColumns })

  it('affiche les colonnes correctement', () => {
    const columns = wrapper.findAll('.p-column')

    expect(columns.length - 1).toBe(patientsListColumns.length)
  })

  it('affiche le nombre total de patients', () => {
    const paginator = wrapper.find('.p-paginator')
    expect(paginator.exists()).toBe(true)
    expect(paginator.text()).toContain('2')
  })

  it('affiche la liste des patients', () => {
    const patients = wrapper.findAll('tbody tr')
    expect(patients.length).toBe(mockPatientsList.length)
  })
})
