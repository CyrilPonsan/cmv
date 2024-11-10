/**
 * @file use-lazy-load.ts
 * @description Composable for handling lazy-loading
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { computed, ref, watch, type Ref, type UnwrapRef } from 'vue'
import useHttp from './use-http'
import type LazyLoadEvent from '@/models/lazy-load-event'
import type LazyState from '@/models/lazy-state'

// Type pour les réponses de l'API
type APIResponse<T> = {
  data: T[]
  total: number
}

// Interface exposée par le composable
type UseLazyLoad<T> = {
  getData: () => void
  lazyState: Ref<LazyState>
  loading: Ref<boolean>
  onFilterChange: (event: Event) => void
  onLazyLoad: (event: LazyLoadEvent) => void
  onResetFilter: () => void
  onSort: (event: LazyLoadEvent) => void
  result: Ref<UnwrapRef<T>[]>
  search: Ref<string>
  totalRecords: Ref<number>
}

const useLazyLoad = <T extends object>(url: string): UseLazyLoad<T> => {
  const http = useHttp()
  const result = ref<UnwrapRef<T>[]>([]) as Ref<UnwrapRef<T>[]>
  const totalRecords = ref<number>(0)
  let timer: NodeJS.Timeout | null = null
  const search = ref<string>('')

  // État de la pagination
  const lazyState = ref<LazyState>({
    first: 0,
    rows: 10,
    sortField: 'nom',
    sortOrder: 1
  })

  // Gestion de l'événement de filtre + debounce
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

  // Réinitialise le filtre global
  const onResetFilter = () => {
    search.value = ''
  }

  // Gestion de l'événement de lazy-loading
  const onLazyLoad = (event: LazyLoadEvent) => {
    lazyState.value = {
      first: event.first,
      rows: event.rows,
      sortField: event.sortField ?? 'nom',
      sortOrder: event.sortOrder as 1 | -1 // Force le type ici
    }
  }

  // Gestion de l'événement de tri des colonnes.
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const onSort = (_event: LazyLoadEvent) => {
    lazyState.value = {
      ...lazyState.value,
      first: 0
    }
  }

  //  Mise en cache du numéro de la page pour optimiser les performances de rendu
  const page = computed(() => lazyState.value.first / lazyState.value.rows + 1)

  //  Mise en cache de l'ordre de tri pour optimiser les performances de rendu
  const direction = computed(() => (lazyState.value.sortOrder === 1 ? 'asc' : 'desc'))

  /**
   * Retourne la liste des dossiers administratifs des patients de la clinique
   * Montvert.
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

  // Retourne les données filtrées en fonction de la chaîne de caractères passée en paramètre
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

  //  Envoie une requête à l"API lorsque l'une des valeurs liées à la pagination ou au filtre est mise à jour
  watch([lazyState, search], () => {
    console.log('watching...')

    if (search.value) {
      searchData(search.value)
    } else {
      getData()
    }
  })

  // Retourne l'interface publique du composable
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
