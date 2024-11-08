<script setup lang="ts">
import type Document from '@/models/document'
import Button from 'primevue/button'
import Card from 'primevue/card'
import { useI18n } from 'vue-i18n'

type Props = {
  document: Document
  documentIndex: number
}

const { d } = useI18n()

const { document, documentIndex } = defineProps<Props>()
</script>

<template>
  <Card>
    <template #title>Document {{ documentIndex + 1 }}</template>
    <template #subtitle>
      <p class="text-sm italic mb-2">{{ d(new Date(document.created_at), 'short') }}</p>
    </template>
    <template #content>{{ document.type_document }}</template>
    <template #footer>
      <span class="flex gap-x-4 mt-1">
        <Button label="Télécharger" icon="pi pi-download" />
        <Button label="Supprimer" severity="warn" icon="pi pi-trash" />
      </span>
    </template>
  </Card>
</template>
