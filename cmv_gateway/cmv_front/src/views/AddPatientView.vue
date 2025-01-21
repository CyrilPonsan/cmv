<script setup lang="ts">
// Import des composants nécessaires
import PatientForm from '@/components/create-update-patient/PatientForm.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDataDisclaimer from '@/components/create-update-patient/PatientDataDisclaimer.vue'

// Import des composables et utilitaires
import usePatientForm from '@/composables/usePatientForm'
import { useI18n } from 'vue-i18n'

/**
 * @file AddPatientView.vue
 * @description Vue permettant d'ajouter un nouveau patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Récupération des fonctionnalités du formulaire patient
const { civilites, isLoading, onCreatePatient, schema } = usePatientForm(null)

// Initialisation du composable i18n pour les traductions
const { t } = useI18n()
</script>

<template>
  <!-- En-tête de la page -->
  <section class="mb-16">
    <PageHeader :title="t('patients.add.title')" :description="t('patients.add.description')" />
  </section>

  <!-- Contenu principal -->
  <div class="grid grid-cols-1 2xl:grid-cols-2 gap-16 mb-16">
    <!-- Section du formulaire -->
    <section class="flex justify-center items-start">
      <PatientForm
        :isLoading="isLoading"
        :onSubmit="onCreatePatient"
        :schema="schema"
        :civilites="civilites"
      />
    </section>

    <!-- Section d'avertissement sur les données -->
    <section class="flex justify-center items-center">
      <article class="w-5/6 p-4 flex flex-col border border-neutral-200/50 rounded-lg">
        <PatientDataDisclaimer />
      </article>
    </section>
  </div>
</template>
