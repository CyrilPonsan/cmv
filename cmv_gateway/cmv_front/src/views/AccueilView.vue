<template>
  <div class="flex flex-col gap-y-8 text-xs">
    <PageHeader :title="t('patients.home.title')" :description="t('patients.home.description')" />
    <ListPatients :columns="columns" :patientsList="patientsList" />
  </div>
</template>

<script setup lang="ts">
import ListPatients from '@/components/ListPatients.vue'
import PageHeader from '@/components/PageHeader.vue'
import usePatientList from '@/composables/use-patients-list'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { columns, patientsList, getPatientsList } = usePatientList()

onMounted(() => {
  getPatientsList()
})
</script>
