/**
 * @file useListPatients.ts
 * @description Composable pour gérer la liste des patients avec fonctionnalités de pagination, tri et suppression
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import type SuccessWithMessage from '@/models/success-with-message'
import useHttp from './useHttp'
import { useToast, type DataTablePageEvent, type DataTableSortEvent } from 'primevue'
import { useI18n } from 'vue-i18n'
import useLazyLoad from './useLazyLoad'
import type PatientsListItem from '@/models/patients-list-item'
import { onBeforeMount, watch, type Ref, type UnwrapRef } from 'vue'

/**
 * Interface définissant les retours du composable
 */
type ListPatientsReturn = {
  onTrash: (patientId: number) => void // Fonction de suppression d'un patient
  handlePage: (event: DataTablePageEvent) => void // Gestionnaire de pagination
  handleSort: (event: DataTableSortEvent) => void // Gestionnaire de tri
  search: Ref<string> // Terme de recherche
  onResetFilter: () => void // Réinitialisation des filtres
  result: Ref<UnwrapRef<PatientsListItem>[]> // Liste des patients
  totalRecords: Ref<number> // Nombre total d'enregistrements
  lazyState: any // État du lazy loading
  loading: Ref<boolean> // État du chargement
  isLoading: Ref<boolean> // État du chargement (requêtes HTTP)
  error: Ref<string | null> // Message d'erreur éventuel
}

/**
 * Composable pour gérer la liste des patients
 * @returns Interface ListPatientsReturn
 */
const useListPatients = (): ListPatientsReturn => {
  // Composables
  const { t } = useI18n()
  const toast = useToast()
  const { sendRequest, isLoading, error } = useHttp()

  // Utilisation du composable de lazy loading
  const {
    getData,
    lazyState,
    loading,
    onResetFilter,
    onLazyLoad,
    onSort,
    search,
    result,
    totalRecords
  } = useLazyLoad<PatientsListItem>('/patients/patients')

  /**
   * Gère la suppression d'un patient
   * @param patientId - ID du patient à supprimer
   */
  const onTrash = (patientId: number) => {
    console.log('onTrash', patientId)
    const applyData = (data: SuccessWithMessage) => {
      if (data.success) {
        toast.add({
          severity: 'success',
          life: 5000,
          summary: t('patients.home.toasters.delete.success.summary'),
          detail: t(`api.${data.message}`),
          closable: true
        })
        getData()
      }
    }
    sendRequest(
      {
        path: `/patients/delete/patients/${patientId}`,
        method: 'delete'
      },
      applyData
    )
  }

  // Chargement initial des données au montage du composant
  onBeforeMount(() => getData())

  /**
   * Wrapper pour la gestion de la pagination
   * @param event - Événement de pagination
   */
  const handlePage = (event: DataTablePageEvent) => {
    onLazyLoad(event as any)
  }

  /**
   * Wrapper pour la gestion du tri
   * @param event - Événement de tri
   */
  const handleSort = (event: DataTableSortEvent) => {
    onSort(event as any)
  }

  watch(error, (newValue) => {
    console.log('error updated:', newValue)
    if (newValue?.length) {
      toast.add({
        severity: 'error',
        life: 5000,
        summary: t('patients.home.toasters.delete.error.summary'),
        detail: t(`api.${newValue}`),
        closable: true
      })
    }
  })

  return {
    onTrash,
    handlePage,
    handleSort,
    search,
    onResetFilter,
    result,
    totalRecords,
    lazyState,
    loading,
    isLoading,
    error
  }
}

export default useListPatients
