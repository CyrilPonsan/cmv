<script setup lang="ts">
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import FileUpload from 'primevue/fileupload'
import Select from 'primevue/select'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

type DocumentType = {
  label: string
  value: string
}

const { fullname, loading, visible } = defineProps<{
  fullname: string
  loading: boolean
  visible: boolean
}>()
const { t } = useI18n()

const documentTypes = ref<DocumentType[]>([
  {
    label: t('patients.detail.documents.document_types.health_insurance_card_certificate'),
    value: 'health_insurance_card_certificate'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_care'),
    value: 'authorization_for_care'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_treatment'),
    value: 'authorization_for_treatment'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_visit'),
    value: 'authorization_for_visit'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_overnight_stay'),
    value: 'authorization_for_overnight_stay'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_departure'),
    value: 'authorization_for_departure'
  },
  {
    label: t('patients.detail.documents.document_types.authorization_for_disconnection'),
    value: 'authorization_for_disconnection'
  },
  { label: t('patients.detail.documents.document_types.miscellaneous'), value: 'miscellaneous' }
])

const selectedDocumentType = ref<DocumentType | null>(null)
const selectedFile = ref<File | null>(null)

const isValid = computed(() => selectedFile.value && selectedDocumentType.value)

const onSubmit = (): void => {
  console.log(selectedDocumentType.value)
  if (selectedFile.value && selectedDocumentType.value) {
    const formData = new FormData()
    formData.append('document_type', selectedDocumentType.value.value)
    formData.append('file', selectedFile.value)

    emit('upload:submit', formData)
  }
}

const onSelect = (event: any): void => {
  const file = event.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'upload:submit', form: FormData): void
}>()
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    header="Téléverser un document"
    :style="{ width: '40rem' }"
    @update:visible="emit('update:visible', false)"
  >
    <span class="text-surface-500 dark:text-surface-400 flex gap-x-2 items-center mb-8">
      <p>Dossier administratif de :</p>
      <p class="capitalize">{{ fullname }}</p>
    </span>
    <form class="flex flex-col gap-y-4" @submit.prevent="onSubmit">
      <Select
        name="document-type"
        v-model="selectedDocumentType"
        :options="documentTypes"
        optionLabel="label"
        placeholder="Sélectionner un type de document"
        class="w-full"
      />
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

        <template #empty>
          <br />
          <span>Glissez et déposez un fichier PDF ici (max 3Mo)</span>
        </template>
      </FileUpload>

      <span class="w-full flex items-center gap-x-4">
        <Button
          class="w-full"
          label="Téléverser"
          type="submit"
          :disabled="!isValid"
          :loading="loading"
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
