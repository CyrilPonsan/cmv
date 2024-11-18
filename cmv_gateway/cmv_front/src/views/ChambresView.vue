<template>
  <main class="flex flex-col gap-y-4">
    <div class="flex gap-x-4 items-center">
      <h1 class="text-2xl font-bold">Liste des chambres</h1>
      <Button
        icon="pi pi-refresh"
        text
        aria-label="rafraîchir la liste des chambres"
        :loading="http.isLoading.value"
        :disabled="http.isLoading.value"
        @:click="getChambres"
      />
    </div>
    <div class="flex flex-col gap-y-24 mt-4">
      <div v-for="service in services" v-bind:key="service.id">
        <ServiceItem v-bind:service="service" />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import ServiceItem from '@/components/ServiceItem.vue'
import useHttp from '@/composables/useHttp'
import type Service from '@/models/service'
import Button from 'primevue/button'
import { onBeforeMount, ref } from 'vue'

const services = ref<Service[]>([])
const http = useHttp()

/**
 * retourne la liste des services et des chambres associées
 */
const getChambres = async () => {
  const applyData = (data: Service[]) => {
    services.value = data
  }
  http.sendRequest(
    {
      path: '/home/services'
    },
    applyData
  )
}

onBeforeMount(() => getChambres())
</script>
