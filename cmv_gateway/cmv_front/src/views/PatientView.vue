<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import PatientDetail from '@/components/PatientDetail.vue'
import useHttp from '@/composables/use-http'
import type DetailPatient from '@/models/detail-patient'
import Button from 'primevue/button'
import { onBeforeMount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const http = useHttp()
const route = useRoute()

const detailPatient = ref<DetailPatient | null>(null)

const applyData = (data: DetailPatient) => {
  detailPatient.value = data
}

onBeforeMount(() => {
  http.sendRequest<DetailPatient>(
    { path: `/patients/patients/detail/${route.params.id}` },
    applyData
  )
})
</script>

<template>
  <main class="flex flex-col gap-y-8">
    <section>
      <PageHeader
        :title="t('patients.home.title')"
        :description="t('patients.detail.description')"
      />
    </section>
    <section class="grid grid-cols-3 gap-x-8">
      <article v-if="detailPatient" class="col-span-2 p-4 rounded-lg">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold">{{ t('patients.detail.h2') }}</h2>
          <span class="flex gap-x-2 items-center">
            <Button :label="t('patients.detail.button.create_admission')" icon="pi pi-plus" />
            <Button :label="t('patients.detail.button.edit')" icon="pi pi-pencil" severity="info" />
          </span>
        </div>
        <PatientDetail :detail-patient="detailPatient" />
      </article>
      <article class="col-span-1 p-4 rounded-lg border border-surface-500/20">
        <h2 class="text-lg font-bold">{{ t('patients.detail.documents.uploaded_documents') }}</h2>
      </article>
    </section>
  </main>
</template>
