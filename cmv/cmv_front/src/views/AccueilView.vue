<template>
  <div class="flex flex-col gap-y-2">
    <p>coucou les gens de l'accueil !</p>

    {{ patientsList.length }}

    <ListPatients :columns="columns" :patientsList="patientsList" />
  </div>
</template>

<script setup lang="ts">
import ListPatients from '@/components/ListPatients.vue'
import usePatientList from '@/composables/use-patients-list'
import { onMounted } from 'vue'

const { columns, patientsList, getPatientsList } = usePatientList()

onMounted(() => {
  getPatientsList()
})
</script>
