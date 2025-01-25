<script setup lang="ts">
/**
 * @file DocumentUploadDialog.vue
 * @description Composant de dialogue pour téléverser des documents administratifs
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import useUploadDocument from '@/composables/useUploadDocument'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import FileUpload from 'primevue/fileupload'
import Select from 'primevue/select'
import { useI18n } from 'vue-i18n'

type Emits = {
  (e: 'refresh', message: string, patientId: number): void
  (e: 'update:visible', value: boolean): void
}

// Props du composant
const { fullname, patientId, visible } = defineProps<{
  fullname: string // Nom complet du patient
  patientId: number // Identifiant du patient
  visible: boolean // Visibilité du dialogue
}>()

const { t } = useI18n()

const emit = defineEmits<Emits>()

// Récupération des fonctions du composable
const {
  documentTypes,
  isLoading,
  isValid,
  onSubmit,
  onSelect,
  selectedDocumentType,
  selectedFile
} = useUploadDocument(patientId, emit)

const handleSubmit = () => {
  onSubmit()
}
</script>

<template>
  <!-- Dialogue modal -->
  <Dialog
    :visible="visible"
    modal
    :header="t('components.documentsList.upload_dialog.header')"
    :style="{ width: '40rem' }"
    @update:visible="emit('update:visible', false)"
  >
    <!-- En-tête avec le nom du patient -->
    <span class="text-surface-500 dark:text-surface-400 flex gap-x-2 items-center mb-8">
      <p>{{ t('components.documentsList.upload_dialog.content') }}</p>
      <p class="capitalize">{{ fullname }}</p>
    </span>
    <!-- Formulaire de téléversement -->
    <form class="flex flex-col gap-y-4" @submit.prevent="handleSubmit">
      <!-- Sélection du type de document -->
      <Select
        name="document-type"
        v-model="selectedDocumentType"
        :options="documentTypes"
        optionLabel="label"
        :placeholder="t('components.documentsList.upload_dialog.placeholder')"
        class="w-full"
      />
      <!-- Zone de téléversement de fichier -->
      <FileUpload
        name="file"
        :customUpload="true"
        :multiple="false"
        accept="application/pdf"
        :maxFileSize="3000000"
        :previewWidth="0"
        :chooseLabel="t('components.documentsList.upload_dialog.buttons.choose_label')"
        :showUploadButton="false"
        :showCancelButton="false"
        :invalidFileSizeMessage="t('components.documentsList.upload_dialog.invalid_file_size')"
        :invalidFileTypeMessage="t('components.documentsList.upload_dialog.invalid_file_type')"
        @select="onSelect"
      >
        <!-- Affichage du fichier sélectionné -->
        <template #content="{ files, removeFileCallback }">
          <div v-if="files.length > 0" class="flex items-center gap-x-2">
            <span class="truncate flex-1">{{ files[0].name }}</span>
            <Button
              icon="pi pi-times"
              text
              rounded
              severity="danger"
              @click="
                () => {
                  selectedFile = null
                  removeFileCallback(0)
                }
              "
              aria-label="Supprimer le fichier"
            />
          </div>
        </template>

        <!-- Message par défaut -->
        <template #empty>
          <br />
          <span>{{ t('components.documentsList.upload_dialog.empty') }}</span>
        </template>
      </FileUpload>

      <!-- Boutons d'action -->
      <span class="w-full flex items-center gap-x-4">
        <Button
          class="w-full"
          :label="t('components.documentsList.upload_dialog.buttons.upload')"
          type="submit"
          :disabled="!isValid"
          :loading="isLoading"
        />
        <Button
          class="w-full"
          label="Annuler"
          severity="warn"
          text
          @click="emit('update:visible', false)"
        />
      </span>
    </form>
  </Dialog>
</template>
