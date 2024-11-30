import { ref, type Ref } from 'vue'
import useHttp from './useHttp'
import { useToast } from 'primevue'
import type SuccessWithMessage from '@/models/success-with-message'
import type { CreatePatient } from '@/models/detail-patient'

type PatientForm = {
  isLoading: Ref<boolean>
  onSubmit: (body: CreatePatient) => void
}

const usePatientForm = (): PatientForm => {
  const { isLoading, sendRequest } = useHttp()
  const toast = useToast()

  const civilites = ref(['Monsieur', 'Madame', 'Autre'])

  const onSubmit = (body: CreatePatient) => {
    const applyData = (data: SuccessWithMessage) => {
      if (data.success) {
        toast.add({
          summary: 'Patient ajouté',
          detail: data.message,
          severity: 'success',
          closable: true,
          life: 5000
        })
      }
    }

    sendRequest<SuccessWithMessage>(
      { path: '/patients/patients', method: 'POST', data: body },
      applyData
    )
  }

  return { isLoading, onSubmit }
}

export default usePatientForm
