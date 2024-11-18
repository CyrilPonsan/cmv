/**
 * @file usePatient.ts
 * @description Composable pour gérer les données d'un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { ref } from 'vue'
import type DetailPatient from '@/models/detail-patient'
import useHttp from '@/composables/useHttp'

/**
 * Hook pour gérer les données d'un patient
 * @param patientId - L'identifiant du patient
 * @returns Un objet contenant les données du patient et une fonction pour les récupérer
 */
export default function usePatient(patientId: string) {
  const { sendRequest } = useHttp()
  // Référence peu profonde pour stocker les détails du patient
  const detailPatient = ref<DetailPatient | null>(null)

  /**
   * Récupère les données du patient depuis l'API
   */
  const fetchPatientData = () => {
    // Fonction de callback pour mettre à jour les données du patient
    const applyData = (data: DetailPatient) => {
      detailPatient.value = data
    }
    // Envoi de la requête à l'API
    sendRequest<DetailPatient>({ path: `/patients/patients/detail/${patientId}` }, applyData)
  }

  return {
    detailPatient,
    fetchPatientData
  }
}
