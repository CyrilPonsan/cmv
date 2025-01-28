<script setup lang="ts">
/**
 * @file PatientView.vue
 * @description Vue détaillée d'un patient permettant de voir et modifier ses informations et documents
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants
import DocumentsList from '@/components/documents/DocumentsList.vue'
import DocumentUpload from '@/components/documents/DocumentUploadDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDetail from '@/components/PatientDetail.vue'
import PatientActions from '@/components/patient/PatientActions.vue'
import PatientForm from '@/components/create-update-patient/PatientForm.vue'

// Import des composables et utilitaires
import usePatient from '@/composables/usePatient'
import useDocuments from '@/composables/useDocuments'
import usePatientForm from '@/composables/usePatientForm'

// Import des composables Vue
import { computed, onBeforeMount, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import LatestAdmission from '@/components/LatestAdmission.vue'

// Initialisation des composables
const { t } = useI18n()
const route = useRoute()

// Récupération des fonctionnalités liées au patient
const { detailPatient, fetchPatientData } = usePatient()
// Gestion des documents (upload, visibilité)
const { visible, toggleVisible, handleUploadSuccess } = useDocuments(fetchPatientData)
// Gestion du formulaire de modification du patient
const { civilites, isEditing, isLoading, onUpdatePatient, schema } =
  usePatientForm(fetchPatientData)

// Calcul du nom complet du patient pour l'affichage
const fullName = computed(() => {
  if (!detailPatient.value) return ''
  return `${detailPatient.value.prenom} ${detailPatient.value.nom}`
})

// Chargement initial des données du patient
onBeforeMount(() => {
  if (route.params.id) {
    fetchPatientData(+route.params.id)
  }
})

watchEffect(() => {
  console.log(detailPatient.value?.id_patient)
})
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
    <section class="w-full flex flex-col xl:flex-row gap-x-4 xl:gap-x-8 gap-y-4">
      <!-- Formulaire d'édition du patient -->
      <article
        v-if="isEditing && detailPatient"
        class="rounded-lg flex flex-col gap-y-4 justify-center items-start"
      >
        <!-- Bascule l'affichage sur la vue détaillée des informations du patient -->
        <p
          class="text-sm font-normal text-primary-500 underline cursor-pointer"
          @click="isEditing = false"
        >
          Retour aux informations du patient
        </p>
        <PatientForm
          :patientDetail="detailPatient"
          :isLoading="isLoading"
          :onSubmit="onUpdatePatient"
          :schema="schema"
          :civilites="civilites"
        />
      </article>

      <!-- Détails du patient en mode lecture -->
      <article v-if="detailPatient && !isEditing" class="w-full xl:w-4/6 p-4 rounded-lg">
        <!-- Titre et boutons d'action -->
        <div class="flex justify-between items-center gap-y-2 mb-4">
          <h2 class="text-lg font-bold">{{ t('patients.detail.h2') }}</h2>
          <PatientActions @toggle-editing="isEditing = $event" />
        </div>
        <!-- Composant affichant les détails du patient -->
        <PatientDetail :detail-patient="detailPatient" />
        <LatestAdmission
          v-if="detailPatient"
          :latestAdmission="detailPatient.latest_admission"
          :patientId="detailPatient.id_patient"
        />
      </article>

      <!-- Section des documents du patient -->
      <article v-if="detailPatient" class="w-full xl:w-2/6 p-4">
        <DocumentsList
          :documents="detailPatient.documents"
          @toggle-visible="toggleVisible"
          @delete-document="fetchPatientData(+route.params.id)"
        />
      </article>

      <!-- Modal de téléversement de documents -->
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
