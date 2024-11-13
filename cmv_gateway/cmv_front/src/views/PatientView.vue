<script setup lang="ts">
/**
 * @file PatientView.vue
 * @description Patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants
import DocumentsList from '@/components/DocumentsList.vue'
import DocumentUpload from '@/components/DocumentUploadDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDetail from '@/components/PatientDetail.vue'

// Import des composables et utilitaires
import useHttp from '@/composables/use-http'
import type DetailPatient from '@/models/detail-patient'

// Import des composants PrimeVue
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'

// Import des composables Vue
import { onBeforeMount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

// Initialisation des composables
const { t } = useI18n()
const { sendRequest } = useHttp()
const route = useRoute()
const toast = useToast()

// Références réactives
const detailPatient = ref<DetailPatient | null>(null)
const visible = ref(false)

/**
 * Récupère les informations détaillées du patient et ses documents
 */
const getDocuments = () => {
  const applyData = (data: DetailPatient) => {
    detailPatient.value = data
  }
  sendRequest<DetailPatient>({ path: `/patients/patients/detail/${route.params.id}` }, applyData)
}

/**
 * Callback appelé après un téléversement réussi
 * Affiche un toast de succès et rafraîchit les documents
 * @param message - Message de succès à afficher
 */
const onSubmitRefresh = (message: string) => {
  toast.add({
    summary: 'Téléversement',
    detail: message,
    severity: 'success',
    life: 3000,
    closable: true
  })
  getDocuments()
}

/**
 * Bascule la visibilité de la boîte de dialogue de téléversement
 */
const toggleVisible = () => {
  visible.value = !visible.value
}

// Chargement initial des données
onBeforeMount(() => getDocuments())
</script>

<template>
  <main class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
    <!-- En-tête de la page -->
    <section>
      <PageHeader
        :title="t('patients.home.title')"
        :description="t('patients.detail.description')"
      />
    </section>
    <!-- Section principale avec les détails du patient et ses documents -->
    <section class="grid grid-cols-4 2xl:grid-cols-3 gap-x-4 xl:gap-x-8">
      <!-- Détails du patient -->
      <article v-if="detailPatient" class="col-span-2 p-4 rounded-lg">
        <!-- Titre et boutons d'action -->
        <div
          class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 mb-4"
        >
          <h2 class="text-lg font-bold">{{ t('patients.detail.h2') }}</h2>
          <!-- Boutons d'action -->
          <span class="flex gap-x-4 items-center">
            <Button :label="t('patients.detail.button.create_admission')" icon="pi pi-plus" />
            <Button :label="t('patients.detail.button.edit')" icon="pi pi-pencil" severity="info" />
          </span>
        </div>
        <!-- Composant affichant les détails du patient -->
        <PatientDetail :detail-patient="detailPatient" />
      </article>
      <!-- Liste des documents -->
      <article v-if="detailPatient" class="col-span-2 2xl:col-span-1 p-4">
        <DocumentsList :documents="detailPatient.documents" @toggle-visible="toggleVisible" />
      </article>
    </section>
  </main>
  <!-- Boîte de dialogue de téléversement de documents -->
  <DocumentUpload
    v-if="detailPatient"
    :fullname="`${detailPatient.prenom} ${detailPatient.nom}`"
    :patientId="detailPatient.id_patient"
    :visible="visible"
    @update:visible="visible = $event"
    @refresh="onSubmitRefresh"
  />
</template>
