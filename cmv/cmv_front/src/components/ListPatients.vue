<template>
  <h1>Liste Patients</h1>
  <div>
    <DataTable
      :value="patientsList"
      paginator
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20, 50]"
      tableStyle="min-width: 50rem"
      paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
      currentPageReportTemplate="{first} à {last} de {totalRecords}"
    >
      <Column
        :class="col.field !== 'email' ? 'capitalize' : ''"
        v-for="col of columns"
        :key="col.field"
        :field="col.field"
        :header="col.header"
        :sortable="col.sortable"
      ></Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type PatientsListItem from '@/models/patients-list-item'
import { ref } from 'vue'

type Props = {
  patientsList: PatientsListItem[]
}

const columns = ref([
  {
    field: 'civilite',
    header: 'Civilité',
    sortable: false
  },
  {
    field: 'nom',
    header: 'Nom',
    sortable: true
  },
  {
    field: 'prenom',
    header: 'Prénom',
    sortable: true
  },
  {
    field: 'date_de_naissance',
    header: 'Date de naissance',
    sortable: true
  },
  {
    field: 'telephone',
    header: 'Téléphone',
    sortable: false
  },
  {
    field: 'email',
    header: 'Email',
    sortable: true
  }
])

defineProps<Props>()
</script>
