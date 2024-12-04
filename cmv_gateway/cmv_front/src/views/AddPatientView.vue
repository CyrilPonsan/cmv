<script setup lang="ts">
import PatientForm from '@/components/create-update-patient/PatientForm.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDataDisclaimer from '@/components/create-update-patient/PatientDataDisclaimer.vue'
import usePatientForm from '@/composables/usePatientForm'
import { useI18n } from 'vue-i18n'

/**
 * @file AddPatientView.vue
 * @description Add patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const {
  civilite,
  civilites,
  date_de_naissance,
  isLoading,
  onSubmit,
  schema,
  updateCivilite,
  updateDateDeNaissance
} = usePatientForm()
const { t } = useI18n()
</script>

<template>
  <section class="mb-16">
    <PageHeader :title="t('patients.add.title')" :description="t('patients.add.description')" />
  </section>
  <div class="grid grid-cols-1 2xl:grid-cols-2 gap-16 mb-16">
    <section class="flex justify-center items-start">
      <PatientForm
        :isLoading="isLoading"
        :onSubmit="onSubmit"
        :schema="schema"
        :civilite="civilite"
        :civilites="civilites"
        :date_de_naissance="date_de_naissance"
        :updateCivilite="updateCivilite"
        :updateDateDeNaissance="updateDateDeNaissance"
      />
    </section>
    <section class="flex justify-center items-center">
      <article class="w-5/6 p-4 flex flex-col border border-neutral-200/50 rounded-lg">
        <PatientDataDisclaimer />
      </article>
    </section>
  </div>
</template>
