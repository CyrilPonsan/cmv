/**
 * @file useDocuments.ts
 * @description Composable pour gérer le téléversement de documents
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

/**
 * Hook pour gérer les documents
 * @param refreshData - Fonction pour rafraîchir les données après un téléversement
 * @returns Un objet contenant l'état de visibilité et les fonctions de gestion
 */
export default function useDocuments(refreshData: () => void) {
  // Référence pour contrôler la visibilité de la boîte de dialogue
  const visible = ref(false)
  // Hook pour afficher les notifications toast
  const toast = useToast()
  // Hook pour gérer les traductions
  const { t } = useI18n()

  /**
   * Bascule la visibilité de la boîte de dialogue
   */
  const toggleVisible = () => {
    visible.value = !visible.value
  }

  /**
   * Gère le succès du téléversement d'un document
   * @param message - Message de succès à afficher
   */
  const handleUploadSuccess = (message: string) => {
    console.log('refreshData')

    toast.add({
      summary: 'Téléversement',
      detail: t(`api.${message}`),
      severity: 'success',
      life: 3000,
      closable: true
    })
    refreshData()
  }

  return {
    visible,
    toggleVisible,
    handleUploadSuccess
  }
}
