/* eslint-disable @typescript-eslint/no-unused-vars */
/**
 * @file use-lazy-load.ts
 * @description Composable pour gérer le chargement paresseux (lazy loading) des données
 * avec pagination, tri et recherche
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { computed, ref, watch, type Ref, type UnwrapRef } from 'vue'
import useHttp from './use-http'
import type LazyLoadEvent from '@/models/lazy-load-event'
import type LazyState from '@/models/lazy-state'

/**
 * Type définissant la structure de la réponse de l'API
 * @template T - Type générique pour les données
 */
type APIResponse<T> = {
  data: T[] // Tableau des données
  total: number // Nombre total d'enregistrements
}

/**
 * Interface exposant les fonctionnalités du composable
 * @template T - Type générique pour les données
 */
type UseLazyLoad<T> = {
  getData: () => void // Fonction pour récupérer les données
  lazyState: Ref<LazyState> // État de la pagination
  loading: Ref<boolean> // État du chargement
  onFilterChange: (event: Event) => void // Gestionnaire de changement de filtre
  onLazyLoad: (event: LazyLoadEvent) => void // Gestionnaire de lazy loading
  onResetFilter: () => void // Réinitialisation du filtre
  onSort: (event: LazyLoadEvent) => void // Gestionnaire de tri
  result: Ref<UnwrapRef<T>[]> // Résultats
  search: Ref<string> // Terme de recherche
  totalRecords: Ref<number> // Nombre total d'enregistrements
}

/**
 * Composable pour gérer le chargement paresseux des données
 * @template T - Type générique pour les données
 * @param url - URL de l'API à interroger
 * @returns Interface UseLazyLoad
 */
const useLazyLoad = <T extends object>(url: string): UseLazyLoad<T> => {
  const http = useHttp()
  const result = ref<UnwrapRef<T>[]>([]) as Ref<UnwrapRef<T>[]>
  const totalRecords = ref<number>(0)
  let timer: NodeJS.Timeout | null = null
  const search = ref<string>('')

  // Configuration initiale de l'état de pagination
  const lazyState = ref<LazyState>({
    first: 0, // Premier enregistrement
    rows: 10, // Nombre d'enregistrements par page
    sortField: 'nom', // Champ de tri par défaut
    sortOrder: 1 // Ordre de tri (1: ascendant, -1: descendant)
  })

  /**
   * Gère le changement de filtre avec debounce
   * @param event - Événement de changement
   */
  const onFilterChange = (event: Event) => {
    const element = event.target as HTMLInputElement
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      lazyState.value = {
        ...lazyState.value,
        first: 0
      }
      search.value = element.value
    }, 300)
  }

  /**
   * Réinitialise le filtre de recherche
   */
  const onResetFilter = () => {
    search.value = ''
  }

  /**
   * Gère l'événement de chargement paresseux
   * @param event - Événement de lazy loading
   */
  const onLazyLoad = (event: LazyLoadEvent) => {
    lazyState.value = {
      first: event.first,
      rows: event.rows,
      sortField: event.sortField ?? 'nom',
      sortOrder: event.sortOrder as 1 | -1
    }
  }

  /**
   * Gère l'événement de tri
   * @param _event - Événement de tri
   */
  const onSort = (_event: LazyLoadEvent) => {
    lazyState.value = {
      ...lazyState.value,
      first: 0
    }
  }

  // Calcul du numéro de page actuel
  const page = computed(() => lazyState.value.first / lazyState.value.rows + 1)

  // Conversion de l'ordre de tri en format API
  const direction = computed(() => (lazyState.value.sortOrder === 1 ? 'asc' : 'desc'))

  /**
   * Récupère les données depuis l'API
   */
  const getData = () => {
    const applyData = (data: APIResponse<T>) => {
      result.value = data.data as UnwrapRef<T>[]
      totalRecords.value = data.total
    }
    http.sendRequest<APIResponse<T>>(
      {
        path: `${url}?page=${page.value}&limit=${lazyState.value.rows}&field=${lazyState.value.sortField}&order=${direction.value}`
      },
      applyData
    )
  }

  /**
   * Recherche des données filtrées
   * @param filter - Terme de recherche
   */
  const searchData = (filter: string) => {
    const applyData = (data: APIResponse<T>) => {
      result.value = data.data as UnwrapRef<T>[]
      totalRecords.value = data.total
      if (timer) {
        clearTimeout(timer)
      }
    }
    http.sendRequest<APIResponse<T>>(
      {
        path: `${url}/search?page=${page.value}&limit=${lazyState.value.rows}&field=${lazyState.value.sortField}&order=${direction.value}&search=${filter}`
      },
      applyData
    )
  }

  // Observe les changements d'état pour déclencher les requêtes
  watch([lazyState, search], () => {
    console.log('watching...')

    if (search.value) {
      searchData(search.value)
    } else {
      getData()
    }
  })

  // Interface publique du composable
  return {
    getData,
    lazyState,
    loading: http.isLoading,
    onFilterChange,
    onLazyLoad,
    onResetFilter,
    onSort,
    result,
    search,
    totalRecords
  }
}

export default useLazyLoad
