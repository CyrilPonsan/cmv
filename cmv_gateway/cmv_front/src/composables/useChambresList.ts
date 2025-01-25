import type Service from '@/models/service'
import { ref, watchEffect, watch, type Ref, onBeforeMount } from 'vue'
import useHttp from './useHttp'
import type { AutoCompleteCompleteEvent, AutoCompleteOptionSelectEvent } from 'primevue'
/**
 * Type définissant l'interface du composable useChambresList
 */
type UseChambresList = {
  list: Ref<Service[]>
  isLoading: Ref<boolean>
  error: Ref<string | null>
  getChambres: () => void
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
  // Liste initiale non filtrée des services
  const initialList = ref<Service[]>([])
  // Liste filtrée des services affichés
  const list = ref<Service[]>([])
  const { sendRequest, isLoading, error } = useHttp()
  // Valeur de recherche dans l'autocomplete
  const searchValue = ref<string>('')
  // Suggestions affichées dans l'autocomplete
  const suggestions = ref<string[]>([])
  /**
   * Récupère la liste des services et des chambres associées depuis l'API
   */
  const getChambres = () => {
    const applyData = (data: Service[]) => {
      initialList.value = data
    }
    sendRequest(
      {
        path: '/chambres/services'
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
    suggestions.value = initialList.value
      .filter((service) => service.nom.toLowerCase().startsWith(event.query.toLowerCase()))
      .map((service) => service.nom)
    const updatedList = initialList.value.filter((service) =>
      service.nom.toLowerCase().startsWith(event.query.toLowerCase())
    )
    // Si la recherche n'aboutit pas, on réinitialise la liste des services affichés
    if (updatedList.length > 0) list.value = updatedList
    else list.value = initialList.value
  }

  /**
   * Gère la sélection d'une suggestion dans l'autocomplete
   * Met à jour la valeur de recherche et filtre la liste des services
   */
  const searchBySelect = (event: AutoCompleteOptionSelectEvent) => {
    searchValue.value = event.value
    list.value = initialList.value.filter((service) => service.nom.startsWith(event.value))
  }

  // Met à jour la liste affichée et les suggestions quand la liste initiale change
  watchEffect(() => {
    list.value = initialList.value
    suggestions.value = initialList.value.map((service) => service.nom)
  })

  // Réinitialise la liste et les suggestions quand la recherche est vidée
  watch(searchValue, (value) => {
    if (value.length === 0) {
      list.value = initialList.value
      suggestions.value = initialList.value.map((service) => service.nom)
    }
  })

  // Chargement initial des données
  onBeforeMount(() => getChambres())

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
