<script setup lang="ts">
/**
 * @file DocumentsHeader.vue
 * @description En-tête de la liste des documents avec un bouton pour ajouter un document
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances
import { useI18n } from 'vue-i18n' // Hook pour l'internationalisation
import Button from 'primevue/button' // Composant Button de PrimeVue

// Récupération des fonctions d'internationalisation
const { t } = useI18n()

// Définition des événements émis par le composant
const emit = defineEmits<{
  (e: 'toggle-visible'): void // Event pour afficher/masquer le dialogue d'ajout de document
}>()
</script>

<template>
  <!-- Conteneur principal avec mise en page responsive -->
  <span
    class="w-full flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 pr-2 mb-4"
  >
    <!-- Titre de la section -->
    <h2 class="text-lg font-bold">{{ t('components.documentsList.uploaded_documents') }}</h2>

    <!-- Bouton d'ajout de document -->
    <Button
      :label="t('components.documentsList.add_document')"
      icon="pi pi-paperclip"
      variant="outlined"
      @click="emit('toggle-visible')"
    />
  </span>
</template>
