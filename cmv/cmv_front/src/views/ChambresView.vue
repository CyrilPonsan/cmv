<template>
  <main class="min-h-screen flex flex-col gap-y-4 p-2">
    <div class="flex items-center gap-x-4">
      <h1 class="text-2xl font-bold">Liste des chambres</h1>
      <ButtonWithLoader
        :label="'Refresh'"
        :loadingLabel="'Loading'"
        :loading="http.isLoading.value"
        @:click="getChambres"
      />
    </div>
    <div class="flex flex-col gap-y-24 mt-4">
      <div class="text-xs" v-for="service in services" v-bind:key="service.id">
        <ServiceItem v-bind:service="service" />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import ButtonWithLoader from '@/components/ButtonWithLoader.vue'
import ServiceItem from '@/components/ServiceItem.vue'
import useHttp from '@/hooks/use-http'
import type Service from '@/models/service'
import { onBeforeMount, ref } from 'vue'

const services = ref<Service[]>([])
const http = useHttp()

/**
 * retourne la liste des services et des chambres associées
 */
const getChambres = async () => {
  const applyData = (dataValue: Service[]) => {
    services.value = dataValue
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
