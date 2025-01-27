<script setup lang="ts">
import useHttp from '@/composables/useHttp'
import { Button } from 'primevue'
import { useRoute } from 'vue-router'

const { sendRequest } = useHttp()

const postAdmission = () => {
  const applyData = (data: any) => {
    console.log({ data })
  }
  sendRequest(
    {
      path: '/patients/admissions',
      method: 'POST',
      body: {
        patient_id: patientId,
        ambulatoire: false,
        entree_le: new Date(),
        sortie_prevue_le: new Date(2026, 1, 1),
        service_id: 3
      }
    },
    applyData
  )
}

const route = useRoute()

const patientId = route.params.patientId
</script>

<template>
  <div>
    <h1>Admission</h1>
  </div>
  <Button label="Créer une admission" @click="postAdmission" />
</template>
