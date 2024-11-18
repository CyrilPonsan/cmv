import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type SuccessWithMessage from '@/models/success-with-message'
import useHttp from './useHttp'

// Type pour les documents administratifs
type DocumentType = {
  label: string
  value: string
}

type UseUploadDocument = {
  documentTypes: Ref<DocumentType[]>
  isLoading: Ref<boolean>
  isValid: ComputedRef<boolean>
  onSubmit: () => void
  onSelect: (event: any) => void
  selectedDocumentType: Ref<DocumentType | null>
  selectedFile: Ref<File | null>
}

const useUploadDocument = (patientId: number): UseUploadDocument => {
  const { t } = useI18n()
  const { isLoading, sendRequest } = useHttp()

  // Events émis par le composant
  /*   const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void // Mise à jour de la visibilité
    (e: 'refresh', message: string): void // Rafraîchir la page
  }>() */

  // Liste des types de documents disponibles
  const documentTypes = ref<DocumentType[]>([
    {
      label: t('components.documentsList.document_types.health_insurance_card_certificate'),
      value: 'health_insurance_card_certificate'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_care'),
      value: 'authorization_for_care'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_treatment'),
      value: 'authorization_for_treatment'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_visit'),
      value: 'authorization_for_visit'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_overnight_stay'),
      value: 'authorization_for_overnight_stay'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_departure'),
      value: 'authorization_for_departure'
    },
    {
      label: t('components.documentsList.document_types.authorization_for_disconnection'),
      value: 'authorization_for_disconnection'
    },
    { label: t('components.documentsList.document_types.miscellaneous'), value: 'miscellaneous' }
  ])

  // État du formulaire
  const selectedDocumentType = ref<DocumentType | null>(null)
  const selectedFile = ref<File | null>(null)

  // Validation du formulaire
  const isValid = computed(() => selectedFile.value !== null && selectedDocumentType.value !== null)

  /**
   * Gère la soumission du formulaire
   * Crée un FormData avec le type de document et le fichier sélectionné
   */
  const onSubmit = (): void => {
    if (selectedFile.value && selectedDocumentType.value) {
      const formData = new FormData()
      formData.append('document_type', selectedDocumentType.value.value)
      formData.append('file', selectedFile.value)

      const applyData = (data: SuccessWithMessage) => {
        if (data.success) {
          selectedFile.value = null
          selectedDocumentType.value = null
        }
      }
      sendRequest<any>(
        {
          path: `/patients/upload/documents/create/${patientId}`,
          method: 'POST',
          data: formData,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        },
        applyData
      )
    }
  }

  /**
   * Gère la sélection d'un fichier
   * @param event Événement de sélection de fichier
   */
  const onSelect = (event: any): void => {
    const file = event.files[0]
    if (file) {
      selectedFile.value = file
    }
  }

  return {
    documentTypes,
    isLoading,
    isValid,
    onSubmit,
    onSelect,
    selectedDocumentType,
    selectedFile
  }
}

export default useUploadDocument
