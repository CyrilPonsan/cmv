<script setup lang="ts">
/**
 * @file AdmissionView.vue
 * @description Vue permettant de créer une nouvelle admission pour un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composables et composants nécessaires
import useHttp from '@/composables/useHttp'
import { Button, useToast } from 'primevue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'

// Initialisation des composables
const { sendRequest, error } = useHttp()
const toast = useToast()

/**
 * Crée une nouvelle admission pour le patient
 * Envoie une requête POST au serveur avec les données de l'admission
 */
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

// Surveillance des erreurs pour afficher les notifications
watch(error, (newError) => {
  if (newError && newError.length > 0) {
    toast.add({
      severity: 'error',
      detail: newError,
      life: 3000
    })
  }
})

// Récupération des paramètres de la route
const route = useRoute()

// Extraction de l'ID du patient depuis les paramètres de la route
const patientId = route.params.patientId
</script>

<template>
  <div>
    <h1>Admission</h1>
  </div>
  <Button label="Créer une admission" @click="postAdmission" />
</template>
