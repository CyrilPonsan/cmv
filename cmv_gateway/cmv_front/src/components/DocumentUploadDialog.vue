<script setup lang="ts">
/**
 * @file DocumentUploadDialog.vue
 * @description Composant de dialogue pour téléverser des documents administratifs
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import useHttp from '@/composables/use-http'
import type SuccessWithMessage from '@/models/success-with-message'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import FileUpload from 'primevue/fileupload'
import Select from 'primevue/select'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

// Type pour les documents administratifs
type DocumentType = {
  label: string
  value: string
}

// Props du composant
const { fullname, patientId, visible } = defineProps<{
  fullname: string // Nom complet du patient
  patientId: number // Identifiant du patient
  visible: boolean // Visibilité du dialogue
}>()
const { isLoading, sendRequest } = useHttp()
const { t } = useI18n()

// Liste des types de documents disponibles
const documentTypes = ref<DocumentType[]>([
  {
    label: t('components.documentsList.document_types.health_insurance_card_certificate'),
    value: 'health_insurance_card_certificate'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_care'),
    value: 'authorization_for_care'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_treatment'),
    value: 'authorization_for_treatment'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_visit'),
    value: 'authorization_for_visit'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_overnight_stay'),
    value: 'authorization_for_overnight_stay'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_departure'),
    value: 'authorization_for_departure'
  },
  {
    label: t('components.documentsList.document_types.authorization_for_disconnection'),
    value: 'authorization_for_disconnection'
  },
  { label: t('components.documentsList.document_types.miscellaneous'), value: 'miscellaneous' }
])

// État du formulaire
const selectedDocumentType = ref<DocumentType | null>(null)
const selectedFile = ref<File | null>(null)

// Validation du formulaire
const isValid = computed(() => selectedFile.value && selectedDocumentType.value)

/**
 * Gère la soumission du formulaire
 * Crée un FormData avec le type de document et le fichier sélectionné
 */
const onSubmit = (): void => {
  if (selectedFile.value && selectedDocumentType.value) {
    const formData = new FormData()
    formData.append('document_type', selectedDocumentType.value.value)
    formData.append('file', selectedFile.value)

    const applyData = (data: SuccessWithMessage) => {
      if (data.success) {
        emit('update:visible', false)
        selectedFile.value = null
        selectedDocumentType.value = null
        emit('refresh', data.message)
      }
    }
    sendRequest<any>(
      {
        path: `/patients/upload/documents/create/${patientId}`,
        method: 'POST',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      },
      applyData
    )
  }
}

/**
 * Gère la sélection d'un fichier
 * @param event Événement de sélection de fichier
 */
const onSelect = (event: any): void => {
  const file = event.files[0]
  if (file) {
    selectedFile.value = file
  }
}

// Events émis par le composant
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void // Mise à jour de la visibilité
  (e: 'refresh', message: string): void // Rafraîchir la page
}>()
</script>

<template>
  <!-- Dialogue modal -->
  <Dialog
    :visible="visible"
    modal
    header="Téléverser un document"
    :style="{ width: '40rem' }"
    @update:visible="emit('update:visible', false)"
  >
    <!-- En-tête avec le nom du patient -->
    <span class="text-surface-500 dark:text-surface-400 flex gap-x-2 items-center mb-8">
      <p>Dossier administratif de :</p>
      <p class="capitalize">{{ fullname }}</p>
    </span>
    <!-- Formulaire de téléversement -->
    <form class="flex flex-col gap-y-4" @submit.prevent="onSubmit">
      <!-- Sélection du type de document -->
      <Select
        name="document-type"
        v-model="selectedDocumentType"
        :options="documentTypes"
        optionLabel="label"
        placeholder="Sélectionner un type de document"
        class="w-full"
      />
      <!-- Zone de téléversement de fichier -->
      <FileUpload
        name="file"
        customUpload="true"
        :multiple="false"
        accept="application/pdf"
        :maxFileSize="3000000"
        previewWidth="0"
        chooseLabel="Choisir un fichier"
        :showUploadButton="false"
        :showCancelButton="false"
        invalidFileSizeMessage="Le fichier est trop volumineux (max 3Mo)"
        invalidFileTypeMessage="Le fichier doit être au format PDF"
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
          <span>Glissez et déposez un fichier PDF ici (max 3Mo)</span>
        </template>
      </FileUpload>

      <!-- Boutons d'action -->
      <span class="w-full flex items-center gap-x-4">
        <Button
          class="w-full"
          label="Téléverser"
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
