<script setup lang="ts">
/**
 * @file DeleteConfirmationDialog.vue
 * @description Dialogue de confirmation pour la suppression d'un document
 */

// Import des dépendances
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type Document from '@/models/document'

// Props du composant
const { visible, document, loading } = defineProps<{
  visible: boolean // Contrôle la visibilité du dialogue
  document: Document | null // Document à supprimer
  loading: boolean // État de chargement pendant la suppression
}>()

// Events émis par le composant
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void // Mise à jour de la visibilité
  (e: 'confirm'): void // Confirmation de la suppression
  (e: 'cancel'): void // Annulation de la suppression
}>()

// Hook d'internationalisation
const { t } = useI18n()
</script>

<template>
  <!-- Dialogue modal de confirmation de suppression -->
  <Dialog
    :visible="visible"
    modal
    :header="t('components.documentsList.dialog.header')"
    :style="{ width: '35rem' }"
    @update:visible="emit('cancel')"
  >
    <!-- Contenu du dialogue -->
    <div class="flex flex-col gap-y-2">
      <span class="text-surface-500 dark:text-surface-400 block"></span>
      <!-- Message de confirmation -->
      <p>{{ t('components.documentsList.dialog.content') }}</p>
      <!-- Affichage du type de document à supprimer -->
      <div v-if="document" class="font-bold opacity-50 pl-4">
        - {{ t(`components.documentsList.document_types.${document.type_document}`) }}
      </div>
    </div>
    <!-- Boutons d'action -->
    <div class="w-full flex gap-x-4 mt-12">
      <!-- Bouton de confirmation -->
      <Button
        fluid
        type="button"
        :label="t('components.documentsList.dialog.buttons.confirm')"
        severity="warn"
        :loading="loading"
        @click="emit('confirm')"
      />
      <!-- Bouton d'annulation -->
      <Button
        fluid
        type="button"
        :label="t('components.documentsList.dialog.buttons.cancel')"
        severity="secondary"
        text
        @click="emit('cancel')"
      />
    </div>
  </Dialog>
</template>
