<script setup lang="ts">
/**
 * Tableau affichant la liste des dossiers administratifs des patients
 * de la clinique avec un système de pagination.
 * La pagination fonctionne en mode "lazy-loading".
 * La logique du "lazy-loading" est gérée dans le composable "useLazyLoad".
 */
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'

import type { DataTableFilterMeta } from 'primevue/datatable'
import { patientsListColumns } from '@/libs/columns/patients-list'
import useLazyLoad from '@/composables/use-lazy-load'
import type PatientsListItem from '@/models/patients-list-item'

// Définition des props et des types
const columns = patientsListColumns
const filters = ref<DataTableFilterMeta>({})
const globalFilterValue = ref<string>('')

// Composables
const { t, d } = useI18n()
const toast = useToast()

// Utilisation du composable de lazy loading
const {
  getData,
  lazyState,
  loading,
  onFilterChange,
  onLazyLoad,
  onSort,
  result: patientsList,
  totalRecords
} = useLazyLoad<PatientsListItem>('/patients/patients')

// Gestion du message de suppression
const onTrash = () => {
  toast.add({
    severity: 'warn',
    life: 5000,
    summary: t('patients.home.toasters.delete.summary'),
    detail: t('patients.home.toasters.delete.detail'),
    closable: false
  })
}

// Surveillance de la valeur du filtre global
watch(globalFilterValue, (newValue) => {
  console.log('Nouvelle valeur du filtre global:', newValue)
})

// Chargement initial des données
onMounted(() => getData())
</script>

<template>
  <DataTable
    v-model:filters="filters"
    :value="patientsList"
    :lazy="true"
    :loading="loading"
    :total-records="totalRecords"
    :rows-per-page-options="[5, 10, 20, 50]"
    v-model:first="lazyState.first"
    v-model:rows="lazyState.rows"
    v-model:sort-field="lazyState.sortField"
    v-model:sort-order="lazyState.sortOrder"
    data-key="id_patient"
    :striped-rows="true"
    :paginator="true"
    table-style="min-width: 50rem"
    paginator-template="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
    :current-page-report-template="`${lazyState.first + 1} ${t('pagination.to')} ${lazyState.first + lazyState.rows} ${t('pagination.from')} ${totalRecords}`"
    class="shadow-md"
    @page="onLazyLoad"
    @sort="onSort"
  >
    <!-- En-tête avec barre de recherche -->
    <template #header>
      <div class="flex justify-end rounded-tl-lg rounded-tr-lg">
        <IconField class="flex items-center gap-x-4">
          <InputIcon>
            <i class="pi pi-search opacity-20" />
          </InputIcon>
          <InputText
            type="search"
            v-model="globalFilterValue"
            :placeholder="t('patients.home.placeholder.search')"
            @input="onFilterChange"
          />
        </IconField>
      </div>
    </template>

    <!-- Information sur le nombre total de patients -->
    <template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold">
        {{ t('patients.home.total_patients', totalRecords) }}
      </span>
    </template>

    <!-- Colonnes dynamiques -->
    <Column
      v-for="col of columns"
      :key="col.field"
      :field="col.field"
      :header="t(`columns.patientsList.${col.header}`)"
      :sortable="col.sortable"
    >
      <template #body="slotProps">
        <template v-if="col.field === 'date_de_naissance'">
          {{ d(new Date(slotProps.data[col.field]), 'short') }}
        </template>
        <template v-else>
          <span :class="{ capitalize: col.field !== 'email' }">
            {{ slotProps.data[col.field] }}
          </span>
        </template>
      </template>
    </Column>

    <!-- Colonne d'actions -->
    <Column header="Actions" :exportable="false">
      <template #body>
        <button
          class="p-2 hover:bg-red-100 rounded-full transition-colors"
          @click="onTrash"
          type="button"
        >
          <i class="pi pi-trash text-red-500" />
        </button>
      </template>
    </Column>
    <template #empty>
      <div class="text-center p-4">
        <i class="pi pi-info-circle text-warn text-xl mb-2"></i>
        <p>{{ t('patients.home.placeholder.empty') }}</p>
      </div>
    </template>
  </DataTable>
</template>
