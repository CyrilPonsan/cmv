<script setup lang="ts">
/**
 * Tableau affichant la liste des dossiers administratifs des patients
 * de la clinique avec un système de pagination.
 * La pagination fonctionne en mode "lazy-loading".
 * La logique du "lazy-loading" est gérée dans le composable "useLazyLaod".
 */
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type PatientsListItem from '@/models/patients-list-item'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'
import useLazyLoad from '@/composables/use-lazy-load'
import { patientsListColumns } from '@/libs/columns/patients-list'
import { onMounted } from 'vue'

const columns = patientsListColumns

const { d, t } = useI18n()
const toast = useToast()
const {
  getData,
  lazyState,
  loading,
  onLazyLoad,
  onSort,
  result: patientsList,
  totalRecords
} = useLazyLoad<PatientsListItem>('/patients/patients')

const onTrash = () => {
  toast.add({
    severity: 'warn',
    life: 5000,
    summary: t('patients.home.toasters.delete.summary'),
    detail: t('patients.home.toasters.delete.detail'),
    closable: false
  })
}

// Chargement initial
onMounted(() => getData())
</script>

<template>
  <DataTable
    class="rounded-md shadow-md"
    :value="patientsList"
    :lazy="true"
    :loading="loading"
    :totalRecords="totalRecords"
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
    :currentPageReportTemplate="`${lazyState.first + 1} ${t('pagination.to')} ${lazyState.first + lazyState.rows} ${t('pagination.from')} ${totalRecords}`"
    @page="onLazyLoad"
    @sort="onSort"
  >
    <template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold">
        {{ t('patients.home.total_patients', totalRecords) }}
      </span>
    </template>
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
    <Column header="Actions">
      <template #body>
        <i class="mx-auto pi pi-trash cursor-pointer" style="color: red" @click="onTrash" />
      </template>
    </Column>
  </DataTable>
</template>
