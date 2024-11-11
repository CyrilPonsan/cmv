<script setup lang="ts">
/**
 * @file PatientView.vue
 * @description Patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import DocumentPatient from '@/components/DocumentPatient.vue'
import DocumentUpload from '@/components/DocumentUpload.vue'
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
const visible = ref(false)

const submitDocument = (formData: FormData) => {
  http.sendRequest<any>(
    {
      path: `/patients/upload/documents/create/${route.params.id}`,
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    },
    (data: any) => {
      console.log(data)
    }
  )
}

const toggleVisible = () => {
  console.log('toggling...')

  visible.value = !visible.value
}

onBeforeMount(() => {
  const applyData = (data: DetailPatient) => {
    detailPatient.value = data
  }
  http.sendRequest<DetailPatient>(
    { path: `/patients/patients/detail/${route.params.id}` },
    applyData
  )
})
</script>

<template>
  <main class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
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
      <article class="col-span-1 p-4">
        <span class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold">
            {{ t('patients.detail.documents.uploaded_documents') }}
          </h2>
          <Button
            label="Ajouter un document"
            icon="pi pi-paperclip "
            outlined
            @click="toggleVisible"
          />
        </span>
        <div v-if="detailPatient && detailPatient.documents.length > 0">
          <DocumentPatient
            v-for="(document, documentIndex) of detailPatient.documents"
            class="mb-4"
            :key="document.id_document"
            :documentIndex="documentIndex"
            :document="document"
          />
        </div>
        <div v-else class="w-full h-[75%] flex justify-start items-center gap-x-4">
          <i class="pi pi-exclamation-circle text-5xl" />
          <p>{{ t('patients.detail.documents.no_document') }}</p>
        </div>
      </article>
    </section>
  </main>
  <DocumentUpload
    :visible="visible"
    :fullname="`${detailPatient?.prenom} ${detailPatient?.nom}`"
    @update:visible="visible = $event"
    @upload:submit="submitDocument"
  />
</template>
