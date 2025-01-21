<script setup lang="ts">
/**
 * @file DocumentsList.vue
 * @description Composant qui affiche la liste des documents d'un patient avec les fonctionnalités de gestion (ajout, téléchargement, suppression)
 */

// Import des types et composants
import type Document from '@/models/document'
import DocumentPatient from './DocumentPatient.vue'
import useDocumentManagement from '@/composables/useDocumentManagement'
import DocumentsHeader from './DocumentsHeader.vue'
import DeleteConfirmationDialog from './DeleteConfirmationDialog.vue'

// Props du composant
const { documents } = defineProps<{
  documents: Document[] // Liste des documents du patient
}>()

// Events émis par le composant
const emit = defineEmits<{
  (e: 'toggle-visible'): void // Afficher/masquer le dialogue d'ajout
  (e: 'download-document', documentId: number): void // Télécharger un document
  (e: 'delete-document'): void // Supprimer un document
}>()

// Récupération des fonctionnalités de gestion des documents
const { visible, documentToDelete, isLoading, deleteDocument } = useDocumentManagement()

/**
 * Gère la suppression d'un document
 * Appelle la fonction de suppression et émet l'événement de mise à jour
 */
const handleDelete = () => {
  if (documentToDelete.value) {
    deleteDocument(documentToDelete.value.id_document, () => emit('delete-document'))
  }
}

/**
 * Gère l'annulation de la suppression
 * Réinitialise les états du dialogue
 */
const handleCancel = () => {
  documentToDelete.value = null
  visible.value = false
}
</script>

<template>
  <!-- En-tête avec titre et bouton d'ajout -->
  <DocumentsHeader @toggle-visible="emit('toggle-visible')" />

  <!-- Liste des documents -->
  <div v-if="documents.length > 0">
    <DocumentPatient
      v-for="(document, documentIndex) of documents"
      class="mb-4"
      :key="document.id_document"
      :documentIndex="documentIndex"
      :document="document"
      @download-document="emit('download-document', document.id_document)"
      @delete-document="(documentToDelete = document), (visible = true)"
    />
  </div>

  <!-- Message si aucun document -->
  <EmptyDocumentsList v-else />

  <!-- Dialogue de confirmation de suppression -->
  <DeleteConfirmationDialog
    :visible="visible"
    :document="documentToDelete"
    :loading="isLoading"
    @confirm="handleDelete"
    @cancel="handleCancel"
  />
</template>
