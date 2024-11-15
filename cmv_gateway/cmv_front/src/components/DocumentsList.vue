<script setup lang="ts">
// TODO : DÉPLACER LA REQUETE DE SUPPRESSION DANS CE COMPOSANT

/**
 * @file DocumentsList.vue
 * @description Composant pour afficher la liste des documents d'un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type Document from '@/models/document' // Type pour les documents
import { useI18n } from 'vue-i18n' // Hook pour l'internationalisation
import DocumentPatient from './DocumentPatient.vue' // Composant pour afficher un document
import Button from 'primevue/button' // Composant Button de PrimeVue
import { ref } from 'vue'

// Props du composant
const { documents } = defineProps<{
  documents: Document[] // Liste des documents à afficher
}>()

// État du composant
const visible = ref(false)
const documentToDelete = ref<Document | null>(null)
// Events émis par le composant
const emit = defineEmits<{
  (e: 'toggle-visible'): void // Event pour afficher/masquer le dialogue d'upload
  (e: 'download-document', documentId: number): void // Event pour télécharger un document
  (e: 'delete-document'): void // Event pour supprimer un document
}>()

// Récupération des fonctions d'internationalisation
const { t } = useI18n()

const confirmDelete = (documentId: number) => {
  const existingDocument = documents.find((document) => document.id_document === documentId)
  if (existingDocument) {
    visible.value = true
    documentToDelete.value = existingDocument
  }
}

const cancelDelete = () => {
  visible.value = false
  documentToDelete.value = null
}
</script>

<template>
  <!-- En-tête avec titre et bouton d'ajout -->
  <span class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 mb-4">
    <h2 class="text-lg font-bold">
      {{ t('components.documentsList.uploaded_documents') }}
    </h2>
    <!-- Bouton pour ajouter un nouveau document -->
    <Button
      label="Ajouter un document"
      icon="pi pi-paperclip "
      outlined
      @click="emit('toggle-visible')"
    />
  </span>

  <!-- Liste des documents -->
  <div v-if="documents.length > 0">
    <!-- Affichage de chaque document via le composant DocumentPatient -->
    <DocumentPatient
      v-for="(document, documentIndex) of documents"
      class="mb-4"
      :key="document.id_document"
      :documentIndex="documentIndex"
      :document="document"
      @download-document="emit('download-document', document.id_document)"
      @delete-document="confirmDelete(document.id_document)"
    />
  </div>

  <!-- Message affiché si aucun document n'est présent -->
  <div v-else class="w-full h-[75%] flex justify-start items-center gap-x-4">
    <i class="pi pi-exclamation-circle text-5xl" />
    <p>{{ t('patients.detail.documents.no_document') }}</p>
  </div>

  <Dialog
    v-model:visible="visible"
    modal
    header="Suppression d'un document administratif"
    :style="{ width: '25rem' }"
  >
    <span class="text-surface-500 dark:text-surface-400 block mb-8"></span>
    <p>Confirmez la suppression du document :</p>
    <div class="font-bold opacity-50">{{ documentToDelete?.type_document }}</div>
    <div class="flex justify-end gap-2">
      <Button type="button" label="Cancel" severity="secondary" @click="cancelDelete"></Button>
      <Button type="button" label="Save" @click="visible = false"></Button>
    </div>
  </Dialog>
</template>
