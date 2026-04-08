import type Service from '@/models/service'
import { ref, watchEffect, watch, type Ref, onBeforeMount } from 'vue'
import useHttp from './useHttp'
import type { AutoCompleteCompleteEvent, AutoCompleteOptionSelectEvent } from 'primevue'
import { useServices } from '@/stores/services'
import { storeToRefs } from 'pinia'
/**
 * Type définissant l'interface du composable useChambresList
 */
type UseChambresList = {
  list: Ref<Service[]>
  isLoading: Ref<boolean>
  error: Ref<string | null>
  getChambres: (serviceId: number) => void
  search: (event: AutoCompleteCompleteEvent) => void
  searchValue: Ref<string>
  searchBySelect: (event: AutoCompleteOptionSelectEvent) => void
  suggestions: Ref<string[]>
  resetSearchValue: () => void
}

/**
 * Composable gérant la liste des chambres et services
 * Permet de récupérer, filtrer et rechercher les services
 */
const useChambresList = (): UseChambresList => {
  // Liste des services affichés
  const list = ref<Service[]>([])
  const { sendRequest, isLoading, error } = useHttp()
  // Valeur de recherche dans l'autocomplete
  const searchValue = ref<string>('')
  // Suggestions affichées dans l'autocomplete
  const suggestions = ref<string[]>([])

  const store = useServices()
  const { servicesList } = storeToRefs(store)

  /**
   * Récupère la liste des services et des chambres associées depuis l'API
   */
  const getChambres = (serviceId: number) => {
    const applyData = (data: Service[]) => {
      list.value = data
    }
    sendRequest(
      {
        path: '/chambres-liste/services/' + serviceId
      },
      applyData
    )
  }

  /**
   * Réinitialise la valeur de recherche
   */
  const resetSearchValue = () => {
    searchValue.value = ''
  }

  /**
   * Gère la recherche dans l'autocomplete
   * Filtre les suggestions et la liste des services affichés
   */
  const search = (event: AutoCompleteCompleteEvent) => {
    suggestions.value = servicesList.value
      .filter((service) => service.nom.toLowerCase().startsWith(event.query.toLowerCase()))
      .map((service) => service.nom)
    const updatedList = list.value.filter((service) =>
      service.nom.toLowerCase().startsWith(event.query.toLowerCase())
    )
    // Si la recherche n'aboutit pas, on réinitialise la liste des services affichés
    if (updatedList.length > 0) list.value = updatedList
    else list.value = list.value
  }

  /**
   * Gère la sélection d'une suggestion dans l'autocomplete
   * Met à jour la valeur de recherche et filtre la liste des services
   */
  const searchBySelect = (event: AutoCompleteOptionSelectEvent) => {
    searchValue.value = event.value
    const serviceId = servicesList.value.find((s) => s.nom === event.value)?.id_service
    if (serviceId) {
      getChambres(serviceId)
    }
  }

  // Met à jour la liste affichée et les suggestions quand la liste initiale change
  watchEffect(() => {
    suggestions.value = servicesList.value.map((service) => service.nom)
  })

  watchEffect(() => {
    if (servicesList.value && servicesList.value.length > 0)
      getChambres(servicesList.value[0].id_service)
  })

  // Réinitialise la liste et les suggestions quand la recherche est vidée
  watch(searchValue, (value) => {
    if (value.length === 0) {
      suggestions.value = list.value.map((service) => service.nom)
      getChambres(servicesList.value[0].id_service)
    }
  })

  // Chargement initial des données

  return {
    getChambres,
    list,
    isLoading,
    error,
    search,
    searchValue,
    searchBySelect,
    suggestions,
    resetSearchValue
  }
}
export default useChambresList
