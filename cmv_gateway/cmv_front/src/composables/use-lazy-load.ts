/**
 * Ce composable gère la logique de l'affichage de la liste des
 * dossiers administratifs de la clinique Montvert.
 * Les données sont chargées en lazy-loading.
 */

import { ref, watch, type Ref, type UnwrapRef } from 'vue'
import useHttp from './use-http'
import type LazyLoadEvent from '@/models/lazy-load-event'
import type LazyState from '@/models/lazy-state'

type APIResponse<T> = {
  data: T[]
  total: number
}

type UseLazyLoad<T> = {
  getData: () => void
  lazyState: Ref<LazyState>
  loading: Ref<boolean>
  onLazyLoad: (event: LazyLoadEvent) => void
  onSort: (event: LazyLoadEvent) => void
  result: Ref<UnwrapRef<T>[]>
  totalRecords: Ref<number>
}

const useLazyLoad = <T extends object>(url: string): UseLazyLoad<T> => {
  const http = useHttp()
  const result = ref<UnwrapRef<T>[]>([]) as Ref<UnwrapRef<T>[]>
  const totalRecords = ref<number>(0)

  // État de la pagination
  const lazyState = ref<LazyState>({
    first: 0,
    rows: 10,
    sortField: 'nom',
    sortOrder: 1
  })

  // Gestion de l'événement de lazy-loading
  const onLazyLoad = (event: LazyLoadEvent) => {
    lazyState.value = {
      first: event.first,
      rows: event.rows,
      sortField: event.sortField ?? 'nom',
      sortOrder: event.sortOrder as 1 | -1 // Force le type ici
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const onSort = (_event: LazyLoadEvent) => {
    lazyState.value = {
      ...lazyState.value,
      first: 0
    }
  }

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
        path: `${url}?page=${lazyState.value.first / lazyState.value.rows + 1}&limit=${
          lazyState.value.rows
        }&field=${lazyState.value.sortField}&order=${
          lazyState.value.sortOrder === 1 ? 'asc' : 'desc'
        }`
      },
      applyData
    )
  }

  //  Envoie une requête à l"API lorsque l'une des valeurs liées à la pagination est mise à jour
  watch(lazyState, () => getData())

  return { getData, lazyState, loading: http.isLoading, onLazyLoad, onSort, result, totalRecords }
}

export default useLazyLoad
