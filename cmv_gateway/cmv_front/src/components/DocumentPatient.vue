<script setup lang="ts">
/**
 * @file DocumentPatient.vue
 * @description Component for displaying a patient's document
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type Document from '@/models/document' // Type pour les documents
import Button from 'primevue/button' // Composant Button de PrimeVue
import Card from 'primevue/card' // Composant Card de PrimeVue
import { useI18n } from 'vue-i18n' // Hook pour l'internationalisation

// Type pour les props du composant
type Props = {
  document: Document // Le document à afficher
  documentIndex: number // L'index du document dans la liste
}

// Récupération des fonctions d'internationalisation
const { d, t } = useI18n()

// Récupération des props
const { document, documentIndex } = defineProps<Props>()
</script>

<template>
  <!-- Card contenant les informations du document -->
  <Card>
    <!-- Titre de la card : numéro du document -->
    <template #title>{{ t('components.documentsList.document') }} {{ documentIndex + 1 }}</template>

    <!-- Sous-titre : date de création du document -->
    <template #subtitle>
      <p class="text-sm italic mb-1">{{ d(new Date(document.created_at), 'short') }}</p>
    </template>

    <!-- Contenu : type de document -->
    <template #content>{{
      t(`components.documentsList.document_types.${document.type_document}`)
    }}</template>

    <!-- Footer : boutons d'action -->
    <template #footer>
      <span class="flex gap-x-4 mt-2">
        <!-- Bouton de téléchargement -->
        <Button
          :label="t('components.documentsList.download')"
          icon="pi pi-download"
          size="small"
        />
        <!-- Bouton de suppression -->
        <Button
          :label="t('components.documentsList.delete')"
          severity="warn"
          icon="pi pi-trash"
          size="small"
        />
      </span>
    </template>
  </Card>
</template>
