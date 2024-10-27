<script setup lang="ts">
import { ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type PatientsListItem from '@/models/patients-list-item'
import type ColumnItem from '@/models/column-item'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const toast = useToast()

interface LazyLoadEvent {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}

// Définition des props avec interface
interface Props {
  columns: ColumnItem[]
  loading: boolean
  totalRecords: number
  patientsList: PatientsListItem[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  totalRecords: 0,
  patientsList: () => []
})

// Définition des événements
const emit = defineEmits(['lazy-load'])

// État de la pagination
const lazyState = ref({
  first: 0,
  rows: 10,
  sortField: 'nom',
  sortOrder: 1
})

// Gestion de l'événement de lazy-loading
const onLazyLoad = (event: LazyLoadEvent) => {
  lazyState.value = {
    first: event.first,
    rows: event.rows,
    sortField: event.sortField ?? 'nom',
    sortOrder: event.sortOrder
  }
  // Emission de l'événement vers le parent
  emit('lazy-load', lazyState.value)
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const onSort = (_event: LazyLoadEvent) => {
  lazyState.value = {
    ...lazyState.value,
    first: 0
  }
  emit('lazy-load', lazyState.value)
}

const onTrash = () => {
  toast.add({
    severity: 'warn',
    life: 5000,
    summary: t('patients.home.toasters.delete.summary'),
    detail: t('patients.home.toasters.delete.detail'),
    closable: false
  })
}
</script>

<template>
  {{ props.totalRecords }}
  <DataTable
    class="rounded-md shadow-md"
    :value="props.patientsList"
    :lazy="true"
    :loading="props.loading"
    :totalRecords="props.totalRecords"
    :rowsPerPageOptions="[5, 10, 20, 50]"
    v-model:first="lazyState.first"
    v-model:rows="lazyState.rows"
    v-model:sortField="lazyState.sortField"
    v-model:sortOrder="lazyState.sortOrder"
    dataKey="id_patient"
    :stripedRows="true"
    :paginator="true"
    tableStyle="min-width: 50rem"
    paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
    :currentPageReportTemplate="`${lazyState.first + 1} ${t('pagination.to')} ${lazyState.first + lazyState.rows} ${t('pagination.from')} ${props.totalRecords}`"
    @page="onLazyLoad"
    @sort="onSort"
  >
    <template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold">
        {{ t('patients.home.total_patients', props.totalRecords) }}
      </span>
    </template>
    <Column
      v-for="col of props.columns"
      :key="col.field"
      :field="col.field"
      :header="t(`columns.patientsList.${col.header}`)"
      :sortable="col.sortable"
    />
    <Column header="Actions">
      <template #body>
        <i class="mx-auto pi pi-trash cursor-pointer" style="color: red" @click="onTrash" />
      </template>
    </Column>
  </DataTable>
</template>
