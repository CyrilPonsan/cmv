<script setup lang="ts">
/**
 * Landing page de l'interface dédiée aux employés du service
 * accueil.
 * Cette vue affiche la liste des dossiers administratifs des
 * patients de la clinique Montvert.
 */
import ListPatients from '@/components/ListPatients.vue'
import PageHeader from '@/components/PageHeader.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col gap-y-8 text-xs">
    <PageHeader :title="t('patients.home.title')" :description="t('patients.home.description')" />
    <ListPatients />
  </div>
</template>
