<script setup lang="ts">
import usePatientsList from '@/composables/use-patients-list'
import { onMounted } from 'vue'
import PatientsTables from './PatientsTables.vue'

interface LazyLoadEvent {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}

const { columns, getPatientsList, loading, patientsList, totalPatients } = usePatientsList()

const onLazyLoad = (event: LazyLoadEvent) => {
  console.log('triggered')
  getPatientsList(
    event.first / event.rows + 1,
    event.rows,
    event.sortField,
    event.sortOrder === 1 ? 'asc' : 'desc'
  )
}

// Chargement initial
onMounted(() => getPatientsList(1, 10, 'nom', 'asc'))
</script>

<template>
  <PatientsTables
    :columns="columns"
    :patientsList="patientsList"
    :loading="loading"
    :totalRecords="totalPatients"
    @lazy-load="onLazyLoad"
  />
</template>
