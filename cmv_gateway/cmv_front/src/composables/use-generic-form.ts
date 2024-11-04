import { ref, watch, watchEffect, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import axios from 'axios'

type FormField = {
  value: any
  attrs: any
  update: Ref<boolean>
}

type UseFormReturn = {
  formSchema: any
  apiError: Ref<string>
  errors: any
  loading: Ref<boolean>
  fields: Record<string, FormField>
  onSubmit: (e: Event) => Promise<void>
}

interface FormConfig {
  schema: any
  submitEndpoint: string
  onSuccess?: () => void
  successMessage?: {
    summary: string
    detail: string
  }
}

const useGenericForm = (config: FormConfig): UseFormReturn => {
  const { t } = useI18n()
  const toast = useToast()
  const apiError = ref('')
  const loading = ref(false)

  const formSchema = toTypedSchema(config.schema)
  const fields: Record<string, FormField> = {}
  const updateFlags: Record<string, Ref<boolean>> = {}

  // Configuration de la validation du formulaire
  const { values, errors, handleSubmit, defineField, validateField } = useForm({
    validationSchema: formSchema
  })

  // Création dynamique des champs basée sur le schéma
  Object.keys(config.schema.shape).forEach((fieldName) => {
    updateFlags[fieldName] = ref(false)
    const [value, attrs] = defineField(fieldName, {
      validateOnModelUpdate: false
    })

    // Surveillance des changements
    watch(value, async () => {
      if (updateFlags[fieldName].value) {
        await validateField(fieldName)
      }
    })

    fields[fieldName] = {
      value,
      attrs,
      update: updateFlags[fieldName]
    }
  })

  // Gestion de la soumission
  const submitForm = async () => {
    loading.value = true
    try {
      await axios.post(config.submitEndpoint, values)

      if (config.onSuccess) {
        config.onSuccess()
      }

      toast.add({
        severity: 'success',
        life: 5000,
        summary: config.successMessage?.summary || t('success.operation_success'),
        detail: config.successMessage?.detail || t('success.operation_success_detail'),
        closable: false
      })
    } catch (error: any) {
      const errorDetail = error.response.data?.detail
      apiError.value = errorDetail ? t(`error.${errorDetail}`) : t('error.network_issue')

      toast.add({
        severity: 'error',
        life: 5000,
        summary: t('error.error'),
        detail: t('error.operation_failure'),
        closable: false
      })
    } finally {
      loading.value = false
    }
  }

  const onSubmit = handleSubmit(() => {
    submitForm()
  })

  // Surveillance des erreurs
  Object.keys(config.schema.shape).forEach((fieldName) => {
    watchEffect(() => {
      if (errors.value[fieldName]) {
        updateFlags[fieldName].value = true
      }
    })
  })

  return {
    formSchema,
    apiError,
    errors,
    loading,
    fields,
    onSubmit
  }
}

export default useGenericForm
