<script setup lang="ts">
import { useI18n } from 'vue-i18n'

/**
 * @file PatientDataDisclaimer.vue
 * @description Composant affichant les informations légales et les responsabilités concernant la protection des données
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const { t } = useI18n()
</script>

<template>
  <!-- Titre principal -->
  <h3 class="text-primary-500 font-bold mb-3">
    {{ t('components.patient_data_disclaimer.title') }}
  </h3>

  <!-- Section sur le contexte légal -->
  <div class="surface-100 p-3 border-round mb-3">
    <h4 class="text-primary-500 font-bold mt-0">
      {{ t('components.patient_data_disclaimer.legal_context_title') }}
    </h4>
    <p>
      {{ t('components.patient_data_disclaimer.legal_context_text') }}
    </p>

    <!-- Liste des principes RGPD -->
    <ul class="pl-4">
      <li>- {{ t('components.patient_data_disclaimer.principle_1') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.principle_2') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.principle_3') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.principle_4') }}</li>
    </ul>
  </div>

  <!-- Section sur les responsabilités -->
  <div class="surface-100 p-3 border-round mb-3">
    <h4 class="text-primary-500 font-bold mt-0">
      {{ t('components.patient_data_disclaimer.responsibilities_title') }}
    </h4>
    <p>
      {{ t('components.patient_data_disclaimer.responsibilities_text') }}
    </p>
    <!-- Liste des responsabilités de l'employé -->
    <ol class="pl-4">
      <li>- {{ t('components.patient_data_disclaimer.responsibility_1') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.responsibility_2') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.responsibility_3') }}</li>
      <li>- {{ t('components.patient_data_disclaimer.responsibility_4') }}</li>
    </ol>
  </div>
</template>
