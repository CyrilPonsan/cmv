<script setup lang="ts">
/**
 * @file AccueilView.vue
 * @description Accueil view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import ListPatients from '@/components/ListPatients.vue'
import PageHeader from '@/components/PageHeader.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <main class="min-w-screen flex flex-col gap-y-8 text-xs">
    <PageHeader :title="t('patients.home.title')" :description="t('patients.home.description')" />
    <ListPatients />
  </main>
</template>
