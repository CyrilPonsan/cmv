import { ref, watch, type Ref } from 'vue'
import useHttp from './useHttp'
import type SuccessWithMessage from '@/models/success-with-message'
import { toTypedSchema } from '@vee-validate/zod'
import { regexGeneric } from '@/libs/regex'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

type CreatePatientResponse = SuccessWithMessage & {
  id_patient: number
}

type PatientForm = {
  civilites: Ref<string[]>
  isLoading: Ref<boolean>
  onCreatePatient: (body: Record<string, unknown>) => void
  onUpdatePatient: (body: Record<string, unknown>) => void
  schema: ReturnType<typeof toTypedSchema>
}

const usePatientForm = (): PatientForm => {
  const { error, isLoading, sendRequest } = useHttp()
  const toast = useToast()
  const { t } = useI18n()
  const router = useRouter()

  const civilites = ref(['Monsieur', 'Madame', 'Autre', 'Roberto'])

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
          z.enum(['Monsieur', 'Madame', 'Autre', 'Roberto'], {
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

  const onCreatePatient = (data: Record<string, unknown>) => {
    const date = data.date_de_naissance as Date
    const year = date.getFullYear()
    const month = date.getMonth()
    const day = date.getDate()
    const updatedDate = new Date(year, month, day, 12, 0, 0)
    const formData = {
      ...data,
      date_de_naissance: updatedDate,
      civilite:
        typeof data.civilite === 'object' && data.civilite !== null
          ? (data.civilite as { value: string }).value
          : data.civilite
    }

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

    sendRequest<CreatePatientResponse>(
      { path: '/patients/patients', method: 'POST', data: formData },
      applyData
    )
  }

  const onUpdatePatient = (data: Record<string, unknown>) => {
    const date = new Date(data.date_de_naissance as string)

    const year = date.getFullYear()
    const month = date.getMonth()
    const day = date.getDate()

    const updatedDate = new Date(year, month, day, 12, 0, 0)

    const formData = {
      ...data,
      date_de_naissance: updatedDate,
      civilite:
        typeof data.civilite === 'object' && data.civilite !== null
          ? (data.civilite as { value: string }).value
          : data.civilite
    }

    const applyData = (response: CreatePatientResponse) => {
      if (response.success) {
        toast.add({
          summary: 'Patient modifié',
          detail: response.message,
          severity: 'success',
          closable: true,
          life: 5000
        })
      }
    }

    sendRequest<CreatePatientResponse>(
      { path: `/patients/patients/${data.id_patient}`, method: 'PUT', data: formData },
      applyData
    )
  }

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
    isLoading,
    onCreatePatient,
    onUpdatePatient,
    schema
  }
}

export default usePatientForm
