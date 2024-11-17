<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const { t } = useI18n()
const emit = defineEmits<{
  (e: 'toggle-visible'): void
}>()
</script>

<template>
  <span class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 mb-4">
    <h2 class="text-lg font-bold">
      {{ t('components.documentsList.uploaded_documents') }}
    </h2>
    <Button
      :label="t('components.documentsList.add_document')"
      icon="pi pi-paperclip"
      outlined
      @click="emit('toggle-visible')"
    />
  </span>
</template>
