import { ref, watch, type Ref } from 'vue'
import useHttp from './useHttp'
import type SuccessWithMessage from '@/models/success-with-message'
import { toTypedSchema } from '@vee-validate/zod'
import { regexGeneric } from '@/libs/regex'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

// Type pour la réponse de création d'un patient
type CreatePatientResponse = SuccessWithMessage & {
  id_patient: number
}

// Type pour le formulaire patient avec ses propriétés et méthodes
type PatientForm = {
  civilite: Ref<string>
  civilites: Ref<string[]>
  date_de_naissance: Ref<Date | Date[] | (Date | null)[] | null | undefined>
  isLoading: Ref<boolean>
  onSubmit: (body: Record<string, unknown>) => void
  schema: ReturnType<typeof toTypedSchema>
  updateCivilite: (value: string) => void
  updateDateDeNaissance: (value: Date | Date[] | (Date | null)[] | null | undefined) => void
}

// Hook personnalisé pour gérer le formulaire patient
const usePatientForm = (): PatientForm => {
  const { error, isLoading, sendRequest } = useHttp()
  const toast = useToast()
  const { t } = useI18n()
  const router = useRouter()

  // Schéma de validation du formulaire avec Zod
  const schema = toTypedSchema(
    z.object({
      prenom: z
        .string({ required_error: t('error.no_firstname') })
        .regex(regexGeneric, { message: t('error.not_valid_firstname') }),
      nom: z
        .string({ required_error: t('error.no_lastname') })
        .regex(regexGeneric, { message: t('error.not_valid_lastname') }),
      adresse: z.string({ required_error: t('error.no_address') }).regex(regexGeneric, {
        message: t('error.not_valid_address')
      }),
      code_postal: z.string({ required_error: t('error.no_zipcode') }).regex(regexGeneric, {
        message: t('error.not_valid_zipcode')
      }),
      ville: z.string({ required_error: t('error.no_city') }).regex(regexGeneric, {
        message: t('error.not_valid_city')
      }),
      telephone: z.string({ required_error: t('error.no_phone') }).regex(regexGeneric, {
        message: t('error.not_valid_phone')
      }),
      email: z
        .string()
        .email({ message: t('error.not_valid_email') })
        .optional()
        .nullable()
    })
  )

  // Valeurs par défaut pour les champs du formulaire
  const civilites = ref(['Monsieur', 'Madame', 'Autre', 'Roberto'])
  const civilite = ref('Autre')
  const date_de_naissance = ref<Date | Date[] | (Date | null)[] | null | undefined>(
    new Date(1974, 3, 14)
  )

  // Méthode pour mettre à jour la civilité
  const updateCivilite = (value: string) => {
    civilite.value = value
  }

  // Méthode pour mettre à jour la date de naissance
  const updateDateDeNaissance = (value: Date | Date[] | (Date | null)[] | null | undefined) => {
    date_de_naissance.value = value
  }

  // Gestionnaire de soumission du formulaire
  const onSubmit = (data: Record<string, unknown>) => {
    // Préparation des données à envoyer
    const body = {
      ...data,
      civilite: civilite.value,
      date_de_naissance: date_de_naissance.value
    }

    // Callback appelé après la création réussie du patient
    const applyData = (data: CreatePatientResponse) => {
      console.log({ data })

      if (data.success) {
        // Affichage d'un message de succès
        toast.add({
          summary: 'Patient ajouté',
          detail: data.message,
          severity: 'success',
          closable: true,
          life: 5000
        })
        // Redirection vers la page du patient créé
        router.push(`/patient/${data.id_patient}`)
      }
    }

    // Envoi de la requête de création du patient
    sendRequest<CreatePatientResponse>(
      { path: '/patients/patients', method: 'POST', data: body },
      applyData
    )
  }

  // Surveillance des erreurs pour afficher les notifications
  watch(error, (value) => {
    if (value && value.length > 0) {
      toast.add({
        summary: 'Erreur',
        detail: value,
        severity: 'error',
        closable: true,
        life: 5000
      })
    }
  })

  // Retourne les propriétés et méthodes du formulaire
  return {
    civilite,
    civilites,
    date_de_naissance,
    isLoading,
    onSubmit,
    schema,
    updateCivilite,
    updateDateDeNaissance
  }
}

export default usePatientForm
