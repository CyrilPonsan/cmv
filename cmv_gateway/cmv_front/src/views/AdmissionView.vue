<script setup lang="ts">
import useHttp from '@/composables/useHttp'
import { Button } from 'primevue'

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
        patient_id: 2,
        ambulatoire: false,
        entree_le: new Date(),
        sortie_prevue_le: new Date(),
        service_id: 1
      }
    },
    applyData
  )
}
</script>

<template>
  <div>
    <h1>Admission</h1>
  </div>
  <Button label="Créer une admission" @click="postAdmission" />
</template>
