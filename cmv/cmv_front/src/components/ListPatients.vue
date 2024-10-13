<script setup lang="ts">
/**
 * Ce composant affiche la liste des dossiers administratifs des patients
 * La liste est téléchargée en lazy loading et un système de pagination est
 * disponible
 */
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type PatientsListItem from '@/models/patients-list-item'
import type ColumnItem from '@/models/column-item'
import { useToast } from 'primevue/usetoast'
import PageHeader from './PageHeader.vue'

const props = defineProps<{ columns: ColumnItem[]; patientsList: PatientsListItem[] }>()

const toast = useToast()

const onTrash = () => {
  toast.add({
    severity: 'warn',
    life: 5000,
    summary: 'Suppression du patient',
    detail: 'Coming soon...',
    closable: false
  })
}
</script>

<template>
  <PageHeader :title="'Espace administratif'" :description="'Liste des patients'" />
  <DataTable
    class="rounded-md shadow-md"
    sortField="nom"
    :sortOrder="1"
    dataKey="id_patient"
    stripedRows="true"
    :value="props.patientsList"
    paginator
    :rows="10"
    :rowsPerPageOptions="[5, 10, 20, 50]"
    tableStyle="min-width: 50rem"
    paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
    currentPageReportTemplate="{first} à {last} de {totalRecords}"
  >
    <template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold"
        >{{ patientsList.length }}
        <p class="font-normal">patients</p></span
      >
    </template>
    <Column
      :class="col.field !== 'email' ? 'capitalize' : ''"
      v-for="col of columns"
      :key="col.field"
      :field="col.field"
      :header="col.header"
      :sortable="col.sortable"
    ></Column>
    <Column header="Actions">
      <template #body>
        <i
          class="mx-auto pi pi-trash cursor-pointer"
          style="color: red"
          @click="onTrash"
        /> </template
    ></Column>
  </DataTable>
</template>
