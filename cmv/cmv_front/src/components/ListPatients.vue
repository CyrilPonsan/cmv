<template>
  <h1>Liste Patients</h1>
  <DataTable
    class="rounded-lg shadow-md"
    sortField="nom"
    :sortOrder="1"
    v-model:selection="selectedPatients"
    dataKey="id_patient"
    stripedRows="true"
    :value="props.patientsList"
    paginator
    :rows="10"
    :rowsPerPageOptions="[5, 10, 20, 50]"
    tableStyle="min-width: 50rem"
    paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
    currentPageReportTemplate="{first} à {last} de {totalRecords}"
    ><template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold"
        >{{ patientsList.length }}
        <p class="font-normal">patients</p></span
      >
    </template>
    <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
    <Column
      :class="col.field !== 'email' ? 'capitalize' : ''"
      :headerStyle="'bg-blue-500/20'"
      v-for="col of columns"
      :key="col.field"
      :field="col.field"
      :header="col.header"
      :sortable="col.sortable"
    ></Column>
  </DataTable>

  {{ selectedPatients.length }}
  {{ selectedPatients }}
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type PatientsListItem from '@/models/patients-list-item'
import { ref } from 'vue'
import type ColumnItem from '@/models/column-item'

const props = defineProps<{ columns: ColumnItem[]; patientsList: PatientsListItem[] }>()
const selectedPatients = ref([])
</script>
