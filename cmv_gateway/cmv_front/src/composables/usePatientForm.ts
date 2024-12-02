import { ref, watch, type Ref } from 'vue'
import useHttp from './useHttp'
import { useToast } from 'primevue'
import type SuccessWithMessage from '@/models/success-with-message'
import { toTypedSchema } from '@vee-validate/zod'
import { regexGeneric } from '@/libs/regex'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { useRouter } from 'vue-router'

type CreatePatientResponse = SuccessWithMessage & {
  id_patient: number
}

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

const usePatientForm = (): PatientForm => {
  const { error, isLoading, sendRequest } = useHttp()
  const toast = useToast()
  const { t } = useI18n()
  const router = useRouter()

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
        .string({ required_error: t('error.no_email') })
        .email({ message: t('error.not_valid_email') })
    })
  )

  const civilites = ref(['Monsieur', 'Madame', 'Autre', 'Roberto'])
  const civilite = ref('Autre')
  const date_de_naissance = ref<Date | Date[] | (Date | null)[] | null | undefined>(
    new Date(1974, 3, 14)
  )

  const updateCivilite = (value: string) => {
    civilite.value = value
  }

  const updateDateDeNaissance = (value: Date | Date[] | (Date | null)[] | null | undefined) => {
    date_de_naissance.value = value
  }

  const onSubmit = (data: Record<string, unknown>) => {
    const body = {
      ...data,
      civilite: civilite.value,
      date_de_naissance: date_de_naissance.value
    }

    const applyData = (data: CreatePatientResponse) => {
      console.log({ data })

      if (data.success) {
        toast.add({
          summary: 'Patient ajouté',
          detail: data.message,
          severity: 'success',
          closable: true,
          life: 5000
        })
        router.push(`/patient/${data.id_patient}`)
      }
    }

    sendRequest<CreatePatientResponse>(
      { path: '/patients/patients', method: 'POST', data: body },
      applyData
    )
  }

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
