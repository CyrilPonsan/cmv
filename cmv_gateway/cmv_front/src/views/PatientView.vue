<script setup lang="ts">
/**
 * @file PatientView.vue
 * @description Patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants
import DocumentsList from '@/components/documents/DocumentsList.vue'
import DocumentUpload from '@/components/documents/DocumentUploadDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDetail from '@/components/PatientDetail.vue'
import PatientActions from '@/components/patient/PatientActions.vue'

// Import des composables et utilitaires
import usePatient from '@/composables/usePatient'
import useDocuments from '@/composables/useDocuments'

// Import des composables Vue
import { computed, onBeforeMount, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import PatientForm from '@/components/create-update-patient/PatientForm.vue'
import usePatientForm from '@/composables/usePatientForm'

// Initialisation des composables
const { t } = useI18n()
const route = useRoute()

const { detailPatient, fetchPatientData } = usePatient(route.params.id as string)
const { visible, toggleVisible, handleUploadSuccess } = useDocuments(fetchPatientData)
const { civilites, isEditing, isLoading, onUpdatePatient, schema } = usePatientForm()

const fullName = computed(() => {
  if (!detailPatient.value) return ''
  return `${detailPatient.value.prenom} ${detailPatient.value.nom}`
})

watchEffect(() => {
  console.log(isEditing.value)
})

onBeforeMount(fetchPatientData)
</script>

<template>
  <div class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
    <!-- En-tête de la page -->
    <section>
      <PageHeader
        :title="t('patients.home.title')"
        :description="t('patients.detail.description')"
      />
    </section>
    <!-- Section principale avec les détails du patient et ses documents -->
    <section class="grid grid-cols-1 2xl:grid-cols-3 gap-x-4 xl:gap-x-8">
      <article
        v-if="isEditing && detailPatient"
        class="col-span-2 2xl:col-span-1 p-4 rounded-lg flex justify-center items-center"
      >
        <PatientForm
          :patientDetail="detailPatient"
          :isLoading="isLoading"
          :onSubmit="onUpdatePatient"
          :schema="schema"
          :civilites="civilites"
        />
      </article>

      <!-- Détails du patient -->
      <article v-if="detailPatient && !isEditing" class="col-span-2 2xl:col-span-1 p-4 rounded-lg">
        <!-- Titre et boutons d'action -->
        <div
          class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 mb-4"
        >
          <h2 class="text-lg font-bold">{{ t('patients.detail.h2') }}</h2>
          <PatientActions @toggle-editing="isEditing = $event" />
        </div>
        <!-- Composant affichant les détails du patient -->
        <PatientDetail :detail-patient="detailPatient" />
      </article>
      <!-- Liste des documents -->
      <article v-if="detailPatient" class="col-span-2 2xl:col-span-1 p-4">
        <DocumentsList
          :documents="detailPatient.documents"
          @toggle-visible="toggleVisible"
          @delete-document="fetchPatientData"
        />
      </article>
      <!-- Boîte de dialogue de téléversement de documents -->
      <DocumentUpload
        v-if="detailPatient"
        :fullname="fullName"
        :patientId="detailPatient.id_patient"
        :visible="visible"
        @update:visible="visible = $event"
        @refresh="handleUploadSuccess"
      />
    </section>
  </div>
</template>
