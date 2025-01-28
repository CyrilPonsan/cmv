<script setup lang="ts">
/**
 * @file EmptyDocumentsList.vue
 * @description Composant affiché lorsqu'un patient n'a pas de documents
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import du composable pour l'internationalisation
import { useI18n } from 'vue-i18n'

// Récupération des fonctions de traduction
const { t } = useI18n()
</script>

<template>
  <!-- Conteneur principal avec message d'absence de documents -->
  <div
    class="w-full flex justify-start items-center gap-x-4 mt-16 border border-dashed border-primary-500 rounded-lg p-4"
  >
    <!-- Icône d'avertissement -->
    <i class="pi pi-exclamation-circle text-5xl" />
    <!-- Message indiquant l'absence de documents -->
    <p>{{ t('components.documentsList.no_document') }}</p>
  </div>
</template>
