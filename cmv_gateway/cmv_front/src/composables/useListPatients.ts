/**
 * @file useListPatients.ts
 * @description Composable to manage the patient list with pagination, sorting and deletion features
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import type SuccessWithMessage from '@/models/success-with-message'
import useHttp from './useHttp'
import { useToast, type DataTablePageEvent, type DataTableSortEvent } from 'primevue'
import { useI18n } from 'vue-i18n'
import useLazyLoad from './useLazyLoad'
import type PatientsListItem from '@/models/patients-list-item'
import { onBeforeMount, ref, watch, type Ref, type UnwrapRef } from 'vue'

/**
 * Interface defining the composable returns
 */
type ListPatientsReturn = {
  onTrash: (patientId: number) => void // Function to delete a patient
  handlePage: (event: DataTablePageEvent) => void // Pagination handler
  handleSort: (event: DataTableSortEvent) => void // Sort handler
  search: Ref<string> // Search term
  onResetFilter: () => void // Reset filters
  result: Ref<UnwrapRef<PatientsListItem>[]> // List of patients
  totalRecords: Ref<number> // Total number of records
  lazyState: any // Lazy loading state
  loading: Ref<boolean> // Loading state
  isLoading: Ref<boolean> // Loading state (HTTP requests)
  error: Ref<string | null> // Error message if any
  getData: () => void // Function to fetch data
  showDeleteDialog: (patient: PatientsListItem) => void // Function to show delete dialog
  onCancel: () => void // Function to cancel deletion
  onConfirm: () => void // Function to confirm deletion
  selectedPatient: Ref<PatientsListItem | null> // Selected patient for deletion
  dialogVisible: Ref<boolean> // Delete dialog visibility
}

/**
 * Composable to manage the patient list
 * @returns ListPatientsReturn interface
 */
const useListPatients = (): ListPatientsReturn => {
  // Composables
  const { t } = useI18n()
  const toast = useToast()
  const { sendRequest, isLoading, error } = useHttp()
  const dialogVisible = ref(false)
  const selectedPatient = ref<PatientsListItem | null>(null)

  /**
   * Affiche la boîte de dialogue de confirmation de suppression
   * @param patient - Le patient à supprimer
   */
  const showDeleteDialog = (patient: PatientsListItem) => {
    selectedPatient.value = patient
    dialogVisible.value = true
  }

  /**
   * Gère l'annulation de la suppression
   * Réinitialise le patient sélectionné et ferme la boîte de dialogue
   */
  const onCancel = () => {
    selectedPatient.value = null
    dialogVisible.value = false
  }

  /**
   * Gère la confirmation de la suppression
   * Supprime le patient sélectionné et ferme la boîte de dialogue
   */
  const onConfirm = () => {
    onTrash(selectedPatient.value!.id_patient)
  }

  // Using lazy loading composable
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
   * Handles patient deletion
   * @param patientId - ID of the patient to delete
   */
  const onTrash = (patientId: number) => {
    const applyData = (data: SuccessWithMessage) => {
      if (data.success) {
        toast.add({
          severity: 'success',
          life: 5000,
          summary: t('patients.home.toasters.delete.success.summary'),
          detail: t(`api.${data.message}`),
          closable: true
        })
        selectedPatient.value = null
        dialogVisible.value = false
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
   * Wrapper for pagination handling
   * @param event - Pagination event
   */
  const handlePage = (event: DataTablePageEvent) => {
    onLazyLoad(event as any)
  }

  /**
   * Wrapper for sort handling
   * @param event - Sort event
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
      selectedPatient.value = null
      dialogVisible.value = false
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
    error,
    getData,
    showDeleteDialog,
    onCancel,
    onConfirm,
    selectedPatient,
    dialogVisible
  }
}

export default useListPatients
