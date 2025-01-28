<script setup lang="ts">
import useHttp from '@/composables/useHttp'
import { Button, useToast } from 'primevue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const { sendRequest, error } = useHttp()
const toast = useToast()

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
        service_id: 6
      }
    },
    applyData
  )
}

watch(error, (newError) => {
  if (newError && newError.length > 0) {
    toast.add({
      severity: 'error',
      detail: newError,
      life: 3000
    })
  }
})

const route = useRoute()

const patientId = route.params.patientId
</script>

<template>
  <div>
    <h1>Admission</h1>
  </div>
  <Button label="Créer une admission" @click="postAdmission" />
</template>
