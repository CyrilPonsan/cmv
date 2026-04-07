<script setup lang="ts">
/**
 * @file LatestAdmission.vue
 * @description Composant qui affiche la dernière admission d'un patient et permet d'accéder aux fonctionnalités liées aux admissions
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type Admission from '@/models/admission'
import { Button } from 'primevue'
import AdmissionItem from './AdmissionItem.vue'
import { useI18n } from 'vue-i18n'

// Props du composant
const { latestAdmission, patientId } = defineProps<{
  latestAdmission: Admission | null // La dernière admission du patient, null si aucune
  patientId: number // L'ID du patient
}>()

const { t } = useI18n()
</script>

<template>
  <!-- En-tête avec titre et boutons d'action -->
  <div class="flex justify-between items-center my-8">
    <h2 class="text-lg font-bold">Admissions</h2>
    <span class="flex items-center gap-x-4">
      <!-- Bouton pour créer une nouvelle admission -->
      <Button
        as="router-link"
        :to="`/admissions/create/${patientId}`"
        icon="pi pi-plus"
        label="Créer une admission"
        variant="outlined"
        v-show="latestAdmission === null"
      />
      <Button
        icon="pi pi-plus"
        label="Créer une admission"
        variant="outlined"
        iconOnly
        :disabled="true"
        v-show="latestAdmission !== null"
        v-tooltip.bottom="'Une admission existe déjà pour ce patient.'"
        aria-label="Bouton désactiver car une admission est déjà en cours pours ce patient."
      />
    </span>
  </div>

  <!-- Affichage de la dernière admission si elle existe -->
  <AdmissionItem v-if="latestAdmission" :admission="latestAdmission" />

  <!-- Message affiché si aucune admission n'existe -->
  <div class="border border-dashed border-primary-500 rounded-lg p-4" v-else>
    <span class="flex items-center gap-x-4">
      <i class="pi pi-exclamation-circle text-5xl" />
      <p>Aucune admission trouvée</p>
    </span>
  </div>
</template>
