<template>
  <p>coucou les gens de l'accueil !</p>
  <ListPatients :patientsList="patients" />
</template>

<script setup lang="ts">
import ListPatients from '@/components/ListPatients.vue'
import useHttp from '@/composables/use-http'
import type PatientsListItem from '@/models/patients-list-item'
import { onBeforeMount, ref } from 'vue'

const http = useHttp()
const patients = ref<PatientsListItem[]>([])

const getPatients = async () => {
  const applyData = (data: any[]) => {
    patients.value = data
  }
  http.sendRequest({ path: '/patients/patients' }, applyData)
}

onBeforeMount(() => getPatients())
</script>
