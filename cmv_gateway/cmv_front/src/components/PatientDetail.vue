<script setup lang="ts">
import type DetailPatient from '@/models/detail-patient'
import Panel from 'primevue/panel'
import { useI18n } from 'vue-i18n'

const { detailPatient } = defineProps<{
  detailPatient: DetailPatient
}>()

const { d, t } = useI18n()
</script>

<template>
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.fullname')">
    <p class="m-0 mt-4 capitalize">
      {{ detailPatient.civilite }} {{ detailPatient.prenom }} {{ detailPatient.nom }}
    </p>
  </Panel>
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.birth_date')">
    <p class="m-0 mt-4">{{ d(new Date(detailPatient.date_de_naissance), 'short') }}</p>
  </Panel>
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.address')">
    <p class="m-0">{{ detailPatient.adresse }}</p>
    <p class="m-0 capitalize">{{ detailPatient.code_postal }} {{ detailPatient.ville }}</p>
  </Panel>
  <Panel class="mb-4 shadow-sm" :header="t('patients.detail.panel.contact')">
    <div class="m-0 flex items-center gap-x-4">
      <i class="pi pi-phone" style="font-weight: bold"></i>
      <p>:</p>
      <p>{{ detailPatient.telephone }}</p>
    </div>
    <div class="m-0 flex items-center gap-x-4">
      <i class="pi pi-envelope" style="font-weight: bold"></i>
      <p>:</p>
      <p>{{ detailPatient.email ?? t('patients.detail.panel.not_provided') }}</p>
    </div>
  </Panel>
</template>
