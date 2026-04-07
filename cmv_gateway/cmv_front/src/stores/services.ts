import useHttp from '@/composables/useHttp'
import type { ServiceListItem } from '@/models/service'
import { defineStore } from 'pinia'
import { useToast } from 'primevue'
import { computed, onBeforeMount, ref, watch } from 'vue'

export const useServices = defineStore('services', () => {
  const http = useHttp()
  const toast = useToast()
  const servicesList = ref<ServiceListItem[]>([])

  const servicesOptions = computed(() => servicesList.value.map((s) => s.nom))

  const fetchServices = () => {
    if (servicesList.value.length > 0) return

    http.sendRequest<ServiceListItem[]>(
      { path: '/chambres/services/simple', method: 'GET' },
      (data) => {
        servicesList.value = data
      }
    )
  }

  watch(http.error, (newError) => {
    if (newError && newError.length > 0) {
      toast.add({ severity: 'error', detail: newError, life: 3000 })
    }
  })

  onBeforeMount(() => {
    fetchServices()
  })

  return {
    servicesList,
    servicesOptions,
    fetchServices
  }
})
