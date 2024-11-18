<script setup lang="ts">
/**
 * @file PatientActions.vue
 * @description Composant affichant les actions disponibles pour un patient (création d'admission et édition)
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants et hooks nécessaires
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

// Récupération de la fonction de traduction
const { t } = useI18n()
</script>

<template>
  <!-- Conteneur des boutons d'action -->
  <span class="flex gap-x-4 items-center">
    <!-- Bouton de création d'une nouvelle admission -->
    <Button :label="t('patients.detail.button.create_admission')" icon="pi pi-plus" />

    <!-- Bouton d'édition du patient -->
    <Button :label="t('patients.detail.button.edit')" icon="pi pi-pencil" severity="info" />
  </span>
</template>
