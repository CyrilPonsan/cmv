<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import ServiceItem from '@/components/ServiceItem.vue'
import useHttp from '@/composables/useHttp'
import type Service from '@/models/service'
import { InputText } from 'primevue'
import Button from 'primevue/button'
import { onBeforeMount, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const services = ref<Service[]>([])
const http = useHttp()
const { t } = useI18n()
/**
 * retourne la liste des services et des chambres associées
 */
const getChambres = async () => {
  const applyData = (data: Service[]) => {
    services.value = data
  }
  http.sendRequest(
    {
      path: '/chambres/services'
    },
    applyData
  )
}

onBeforeMount(() => getChambres())
</script>

<template>
  <div class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
    <!-- En-tête de la page -->
    <section>
      <PageHeader :title="t('rooms.home.title')" :description="t('rooms.home.description')" />
    </section>

    <section class="flex justify-between items-center">
      <span class="flex items-center gap-x-4">
        <h1 class="text-2xl font-bold">Liste des chambres</h1>
        <Button
          icon="pi pi-refresh"
          text
          aria-label="rafraîchir la liste des chambres"
          :loading="http.isLoading.value"
          :disabled="http.isLoading.value"
          @:click="getChambres"
        />
      </span>
      <div>
        <InputText placeholder="Filtrer par service" />
      </div>
    </section>

    <div class="flex flex-col">
      <ul class="flex flex-col gap-y-4">
        <li v-for="service of services" :key="service.id_service">
          <ServiceItem v-bind="service" />
        </li>
      </ul>
    </div>
  </div>
</template>
