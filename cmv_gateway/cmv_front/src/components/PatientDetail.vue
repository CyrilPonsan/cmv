<script setup lang="ts">
/**
 * @file PatientDetail.vue
 * @description Component for displaying patient details
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type DetailPatient from '@/models/detail-patient' // Type pour les détails du patient
import Panel from 'primevue/panel' // Composant Panel de PrimeVue
import { useI18n } from 'vue-i18n' // Hook pour l'internationalisation

// Récupération des props du composant
const { detailPatient } = defineProps<{
  detailPatient: DetailPatient // Les détails du patient à afficher
}>()

// Récupération des fonctions d'internationalisation
const { d, t } = useI18n()
</script>

<template>
  <!-- Panel affichant le nom complet du patient -->
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.fullname')">
    <p class="m-0 mt-4 capitalize">
      {{ detailPatient.civilite }} {{ detailPatient.prenom }} {{ detailPatient.nom }}
    </p>
  </Panel>

  <!-- Panel affichant la date de naissance -->
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.birth_date')">
    <p class="m-0 mt-4">{{ d(new Date(detailPatient.date_de_naissance), 'short') }}</p>
  </Panel>

  <!-- Panel affichant l'adresse complète -->
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.address')">
    <p class="m-0">{{ detailPatient.adresse }}</p>
    <p class="m-0 capitalize">{{ detailPatient.code_postal }} {{ detailPatient.ville }}</p>
  </Panel>

  <!-- Panel affichant les informations de contact -->
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.contact')">
    <!-- Numéro de téléphone -->
    <div class="m-0 flex items-center gap-x-4">
      <i class="pi pi-phone" style="font-weight: bold"></i>
      <p>:</p>
      <p>{{ detailPatient.telephone }}</p>
    </div>
    <!-- Adresse email -->
    <div class="m-0 flex items-center gap-x-4">
      <i class="pi pi-envelope" style="font-weight: bold"></i>
      <p>:</p>
      <p>{{ detailPatient.email ?? t('patients.detail.panel.not_provided') }}</p>
    </div>
  </Panel>
</template>
