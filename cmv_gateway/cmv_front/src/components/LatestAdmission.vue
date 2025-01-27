<script setup lang="ts">
import type Admission from '@/models/admission'
import { Button } from 'primevue'
import { watchEffect } from 'vue'
import AdmissionItem from './AdmissionItem.vue'

const { latestAdmission } = defineProps<{ latestAdmission: Admission | null }>()

watchEffect(() => {
  console.log(latestAdmission)
})
</script>

<template>
  <div class="flex justify-between items-center my-8">
    <h2 class="text-lg font-bold">Admissions</h2>
    <span class="flex items-center gap-x-4">
      <Button
        as="router-link"
        to="/admissions/create"
        icon="pi pi-plus"
        label="Créer une admission"
        variant="outlined"
      />
      <Button
        v-if="latestAdmission !== null"
        as="router-link"
        to="/admissions/history"
        icon="pi pi-history"
        label="Historique des admissions"
        variant="outlined"
      />
    </span>
  </div>

  <AdmissionItem v-if="latestAdmission" :admission="latestAdmission" />

  <div class="border border-dashed border-primary-500 rounded-lg p-4" v-else>
    <span class="flex items-center gap-x-4">
      <i class="pi pi-exclamation-circle text-5xl" />
      <p>Aucune admission trouvée</p>
    </span>
  </div>
</template>
