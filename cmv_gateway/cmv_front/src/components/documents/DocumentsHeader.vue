<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const { t } = useI18n()
const emit = defineEmits<{
  (e: 'toggle-visible'): void
}>()

const { totalDocuments } = defineProps<{
  totalDocuments: number
}>()
</script>

<template>
  <span
    class="w-full flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 pr-2"
  >
    <span class="flex gap-x-2 items-center">
      <h2 class="text-lg font-bold">{{ t('components.documentsList.uploaded_documents') }}</h2>
      <p>-</p>
      <p class="text-sm font-normal">
        {{ t('components.documentsList.total_documents', totalDocuments) }}
      </p>
    </span>
    <Button
      :label="t('components.documentsList.add_document')"
      icon="pi pi-paperclip"
      @click="emit('toggle-visible')"
    />
  </span>
</template>
