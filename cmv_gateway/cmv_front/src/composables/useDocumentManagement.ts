import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import useHttp from '@/composables/useHttp'
import type Document from '@/models/document'
import type SuccessWithMessage from '@/models/success-with-message'
import { useI18n } from 'vue-i18n'

/**
 * Composable pour la gestion des documents
 * Fournit les fonctionnalités de suppression de documents
 */
export default function useDocumentManagement() {
  // État pour contrôler la visibilité de la boîte de dialogue de confirmation
  const visible = ref(false)
  // Document actuellement sélectionné pour suppression
  const documentToDelete = ref<Document | null>(null)
  // Hooks pour les notifications toast et les requêtes HTTP
  const toast = useToast()
  const { isLoading, sendRequest } = useHttp()
  const { t } = useI18n()

  /**
   * Supprime un document spécifié
   * @param documentId - L'ID du document à supprimer
   * @param onSuccess - Callback à exécuter après une suppression réussie
   */
  const deleteDocument = async (documentId: number, onSuccess: () => void) => {
    /**
     * Traite la réponse de l'API après la suppression
     * @param data - La réponse de l'API contenant le statut et le message
     */
    const applyData = (data: SuccessWithMessage) => {
      if (data.success) {
        // Affiche une notification de succès
        toast.add({
          summary: t('components.documentsList.deletion'),
          detail: t(`api.${data.message}`),
          closable: true,
          life: 3000,
          severity: 'success'
        })
        // Exécute le callback de succès et réinitialise l'état
        onSuccess()
        documentToDelete.value = null
        visible.value = false
      }
    }

    // Envoie la requête de suppression à l'API
    sendRequest<SuccessWithMessage>(
      {
        path: `/patients/delete/documents/delete/${documentId}`,
        method: 'delete'
      },
      applyData
    )
  }

  // Expose les propriétés et méthodes nécessaires
  return {
    visible,
    documentToDelete,
    isLoading,
    deleteDocument
  }
}
