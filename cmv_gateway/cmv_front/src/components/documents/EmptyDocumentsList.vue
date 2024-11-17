<template>
  <div class="w-full h-[75%] flex justify-start items-center gap-x-4">
    <i class="pi pi-exclamation-circle text-5xl" />
    <p>{{ t('components.documentsList.no_document') }}</p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
