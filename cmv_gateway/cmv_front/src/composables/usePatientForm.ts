/**
 * @file usePatientForm.ts
 * @description Composable pour gérer le formulaire de création/modification de patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { ref, watch, type Ref } from 'vue'
import useHttp from './useHttp'
import type SuccessWithMessage from '@/models/success-with-message'
import { toTypedSchema } from '@vee-validate/zod'
import { regexGeneric } from '@/libs/regex'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

// Type pour la réponse de création de patient
type CreatePatientResponse = SuccessWithMessage & {
  id_patient: number
}

// Type pour les données retournées par le composable
type PatientForm = {
  civilites: Ref<string[]>
  isEditing: Ref<boolean>
  isLoading: Ref<boolean>
  onCreatePatient: (body: Record<string, unknown>) => void
  onUpdatePatient: (body: Record<string, unknown>) => void
  schema: ReturnType<typeof toTypedSchema>
}

/**
 * Composable pour gérer le formulaire patient
 * @returns {PatientForm} Objet contenant les données et méthodes du formulaire
 */
const usePatientForm = (fetchPatientData: ((id: number) => void) | null): PatientForm => {
  const { error, isLoading, sendRequest } = useHttp()
  const toast = useToast()
  const { t } = useI18n()
  const router = useRouter()

  // Liste des civilités disponibles
  const civilites = ref(['Monsieur', 'Madame', 'Autre'])
  const isEditing = ref(false)

  // Schéma de validation du formulaire
  const schema = toTypedSchema(
    z.object({
      civilite: z
        .any()
        .transform((val) => {
          if (val && typeof val === 'object' && 'value' in val) {
            return val.value
          }
          return val
        })
        .pipe(
          z.enum(['Monsieur', 'Madame', 'Autre'], {
            errorMap: () => ({ message: t('error.not_valid_civility') })
          })
        ),
      date_de_naissance: z.union([
        z.string({
          required_error: t('error.no_birth_date')
        }),
        z.date({
          required_error: t('error.not_valid_birth_date')
        })
      ]),
      prenom: z
        .string({ required_error: t('error.no_firstname') })
        .regex(regexGeneric, { message: t('error.not_valid_firstname') }),
      nom: z
        .string({ required_error: t('error.no_lastname') })
        .regex(regexGeneric, { message: t('error.not_valid_lastname') }),
      adresse: z
        .string({ required_error: t('error.no_address') })
        .regex(regexGeneric, { message: t('error.not_valid_address') }),
      code_postal: z
        .string({ required_error: t('error.no_zipcode') })
        .regex(regexGeneric, { message: t('error.not_valid_zipcode') }),
      ville: z
        .string({ required_error: t('error.no_city') })
        .regex(regexGeneric, { message: t('error.not_valid_city') }),
      telephone: z
        .string({ required_error: t('error.no_phone') })
        .regex(regexGeneric, { message: t('error.not_valid_phone') }),
      email: z
        .string()
        .email({ message: t('error.not_valid_email') })
        .optional()
        .nullable()
    })
  )

  /**
   * Gère la création d'un nouveau patient
   * @param {Record<string, unknown>} data - Données du formulaire
   */
  const onCreatePatient = (data: Record<string, unknown>) => {
    // Formatage de la date de naissance
    const date = data.date_de_naissance as Date
    const year = date.getFullYear()
    const month = date.getMonth()
    const day = date.getDate()
    const updatedDate = new Date(year, month, day, 12, 0, 0)

    // Préparation des données
    const formData = {
      ...data,
      date_de_naissance: updatedDate,
      civilite:
        typeof data.civilite === 'object' && data.civilite !== null
          ? (data.civilite as { value: string }).value
          : data.civilite
    }

    // Callback après création réussie
    const applyData = (response: CreatePatientResponse) => {
      if (response.success) {
        toast.add({
          summary: 'Patient ajouté',
          detail: response.message,
          severity: 'success',
          closable: true,
          life: 5000
        })
        router.push(`/patient/${response.id_patient}`)
      }
    }

    // Envoi de la requête
    sendRequest<CreatePatientResponse>(
      { path: '/patients/patients', method: 'POST', data: formData },
      applyData
    )
  }

  /**
   * Gère la mise à jour d'un patient existant
   * @param {Record<string, unknown>} data - Données du formulaire
   */
  const onUpdatePatient = (data: Record<string, unknown>) => {
    // Formatage de la date de naissance
    const date = new Date(data.date_de_naissance as string)
    const year = date.getFullYear()
    const month = date.getMonth()
    const day = date.getDate()
    const updatedDate = new Date(year, month, day, 12, 0, 0)

    // Préparation des données
    const formData = {
      ...data,
      date_de_naissance: updatedDate,
      civilite:
        typeof data.civilite === 'object' && data.civilite !== null
          ? (data.civilite as { value: string }).value
          : data.civilite
    }

    // Callback après mise à jour réussie
    const applyData = (response: CreatePatientResponse) => {
      if (response.success) {
        toast.add({
          summary: 'Patient modifié',
          detail: response.message,
          severity: 'success',
          closable: true,
          life: 5000
        })

        // Retour à l'affichage du détail du patient
        isEditing.value = false

        // Vérification que fetchPatientData est une fonction avant de l'appeler
        if (typeof fetchPatientData === 'function' && response.id_patient) {
          fetchPatientData(response.id_patient)
        }
      }
    }

    // Envoi de la requête
    sendRequest<CreatePatientResponse>(
      {
        path: `/patients/patients/${data.id_patient}`,
        method: 'PUT',
        data: formData
      },
      applyData
    )
  }
  // Surveillance des erreurs pour afficher les notifications
  watch(
    () => error.value,
    (newError) => {
      if (newError) {
        toast.add({
          summary: 'Erreur',
          detail: newError,
          severity: 'error',
          closable: true,
          life: 5000
        })
      }
    }
  )

  return {
    civilites,
    isEditing,
    isLoading,
    onCreatePatient,
    onUpdatePatient,
    schema
  }
}

export default usePatientForm
