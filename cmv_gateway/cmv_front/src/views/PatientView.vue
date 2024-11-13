<script setup lang="ts">
/**
 * @file PatientView.vue
 * @description Patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import DocumentsList from '@/components/DocumentsList.vue'
import DocumentUpload from '@/components/DocumentUploadDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import PatientDetail from '@/components/PatientDetail.vue'
import useHttp from '@/composables/use-http'
import type DetailPatient from '@/models/detail-patient'
import type SuccessWithMessage from '@/models/success-with-message'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { onBeforeMount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const { isLoading, sendRequest } = useHttp()
const route = useRoute()
const toast = useToast()

const detailPatient = ref<DetailPatient | null>(null)
const visible = ref(false)

const downloadDocument = async (documentId: number) => {
  console.log('downloading')

  window.open(`http://localhost:8001/api/patients/documents/download/${documentId}`, '_blank')
}

const getDocuments = () => {
  const applyData = (data: DetailPatient) => {
    detailPatient.value = data
  }
  sendRequest<DetailPatient>({ path: `/patients/patients/detail/${route.params.id}` }, applyData)
}

const submitDocument = (formData: FormData) => {
  const applyData = (data: SuccessWithMessage) => {
    if (data.success) {
      toast.add({
        summary: 'Téléversement',
        detail: data.message,
        severity: 'success',
        life: 3000,
        closable: true
      })
      getDocuments()
      toggleVisible()
    }
  }
  sendRequest<any>(
    {
      path: `/patients/upload/documents/create/${route.params.id}`,
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    },
    applyData
  )
}

const toggleVisible = () => {
  visible.value = !visible.value
}

onBeforeMount(() => getDocuments())
</script>

<template>
  <main class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
    <!-- Header -->
    <section>
      <PageHeader
        :title="t('patients.home.title')"
        :description="t('patients.detail.description')"
      />
    </section>
    <!-- Detail patient -->
    <section class="grid grid-cols-4 2xl:grid-cols-3 gap-x-8">
      <article v-if="detailPatient" class="col-span-2 p-4 rounded-lg">
        <!-- Title -->
        <div
          class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-y-2 mb-4"
        >
          <h2 class="text-lg font-bold">{{ t('patients.detail.h2') }}</h2>
          <!-- Actions -->
          <span class="flex gap-x-4 items-center">
            <Button :label="t('patients.detail.button.create_admission')" icon="pi pi-plus" />
            <Button :label="t('patients.detail.button.edit')" icon="pi pi-pencil" severity="info" />
          </span>
        </div>
        <!-- Detail patient -->
        <PatientDetail :detail-patient="detailPatient" />
      </article>
      <!-- Uploaded documents -->
      <article v-if="detailPatient" class="col-span-2 2xl:col-span-1 p-4">
        <DocumentsList
          :documents="detailPatient.documents"
          @toggle-visible="toggleVisible"
          @download-document="downloadDocument"
        />
      </article>
    </section>
  </main>
  <!-- Document upload -->
  <DocumentUpload
    :fullname="`${detailPatient?.prenom} ${detailPatient?.nom}`"
    :loading="isLoading"
    :visible="visible"
    @update:visible="visible = $event"
    @upload:submit="submitDocument"
  />
</template>
