import type Service from '@/models/service'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import useHttp from '@/composables/useHttp'

type ServicesList = Omit<Service, 'chambres'>[]

const { sendRequest } = useHttp()

export const useServiceStore = defineStore('service', () => {
  const servicesList = ref<ServicesList | null>(null)
  const servicesOptions = ref<string[]>([])

  const getServicesList = () => {
    if (servicesList.value && servicesList.value.length > 0) return servicesList.value
    else {
      const applyData = (data: ServicesList) => {
        servicesList.value = data
        servicesOptions.value = data.map((service) => service.nom)
      }
      sendRequest<ServicesList>(
        {
          path: '/chambres/services/simple',
          method: 'GET'
        },
        applyData
      )
    }
  }

  return {
    servicesList,
    servicesOptions,
    getServicesList
  }
})
