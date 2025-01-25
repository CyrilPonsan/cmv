<script setup lang="ts">
/**
 * @file DeletePatientDialog.vue
 * @description Composant de dialogue pour confirmer la suppression d'un dossier patient
 */

// Imports des composants et types nécessaires
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type PatientsListItem from '@/models/patients-list-item'

// Récupération de la fonction de formatage des dates depuis i18n
const { d, t } = useI18n()

// Définition des props du composant
const props = defineProps<{
  patient: PatientsListItem // Informations du patient à supprimer
  visible: boolean // Contrôle de la visibilité du dialogue
  isLoading: boolean // Contrôle de l'état de chargement
}>()

// Définition des événements émis par le composant
const emit = defineEmits<{
  (e: 'confirm'): void // Émis lors de la confirmation de suppression
  (e: 'cancel'): void // Émis lors de l'annulation
}>()
</script>

<template>
  <!-- Dialogue de confirmation de suppression -->
  <Dialog
    :visible="props.visible"
    :header="t('patients.home.dialog.header')"
    :style="{ width: '35rem' }"
    :closable="true"
    @update:visible="emit('cancel')"
  >
    <!-- Corps du dialogue avec les informations du patient -->
    <span class="font-semibold flex gap-x-2">
      <p>
        {{ t('patients.home.dialog.content') }}
      </p>
      <p class="capitalize">{{ props.patient.nom }} {{ props.patient.prenom }},</p>
      <p>né(e) le : {{ d(new Date(props.patient.date_de_naissance), 'short') }}</p>
    </span>
    <div class="mt-4">
      <p>
        {{ t('patients.home.dialog.content-2') }}
      </p>
    </div>

    <!-- Pied du dialogue avec les boutons d'action -->
    <template #footer>
      <div class="w-full flex gap-x-4 mt-12">
        <Button
          fluid
          type="button"
          severity="warn"
          @click="emit('confirm')"
          :disabled="isLoading"
          :loading="isLoading"
          :label="t('patients.home.dialog.button.delete')"
        />
        <Button
          fluid
          severity="secondary"
          variant="text"
          @click="emit('cancel')"
          :label="t('patients.home.dialog.button.cancel')"
        />
      </div>
    </template>
  </Dialog>
</template>
