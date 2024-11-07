<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/use-http'
import Button from 'primevue/button'
import { onBeforeMount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const http = useHttp()
const route = useRoute()

const detailPatient = ref<any>(null)

const applyData = (data: any) => {
  detailPatient.value = data
}

onBeforeMount(() => {
  http.sendRequest({ path: `/patients/patients/detail/${route.params.id}` }, applyData)
})
</script>

<template>
  <main class="flex flex-col gap-y-8">
    <PageHeader :title="t('patients.home.title')" :description="t('patients.detail.description')" />
    <pre>{{ detailPatient ?? 'incoming...' }}</pre>
    <Button as="router-link" to=".." label="Retour" />
  </main>
</template>
