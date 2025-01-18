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
      <pre>{{ services }}</pre>
    </div>
  </main>
</template>

<script setup lang="ts">
import ServiceItem from '@/components/ServiceItem.vue'
import useHttp from '@/composables/useHttp'
import type Service from '@/models/service'
import Button from 'primevue/button'
import { onBeforeMount, ref } from 'vue'

const services = ref<any>([])
const http = useHttp()

/**
 * retourne la liste des services et des chambres associées
 */
const getChambres = async () => {
  const applyData = (data: any) => {
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
