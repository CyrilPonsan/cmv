/**
 * Composable destiné à vérifier la validité des champs du formulaire.
 * Soumet les identifiants à l'API dans le but de connecter l'utilisateur.
 */
import { ref, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { useUserStore } from '@/stores/user'
import { AUTH } from '@/libs/urls'
import axios from 'axios'

type LoginReturn<T> = {
  apiError: Ref<string>
  loading: Ref<boolean>
  onSubmit: (values: T) => Promise<void>
}

const useLogin = <T>(/* method: "post"|"put", path:string */): LoginReturn<T> => {
  const { t } = useI18n()
  const userStore = useUserStore()
  const toast = useToast()
  const apiError = ref('')

  // état du loader
  const loading = ref(false)

  // vérification de la validité des champs du formulaire
  const onSubmit = async (values: T) => {
    loading.value = true
    try {
      await axios.post(`${AUTH}/auth/login`, {
        ...values
      })
      userStore.getUserInfos()
      // affiche un toast attestant du succès de la connexion
      toast.add({
        severity: 'success',
        life: 5000,
        summary: t('success.connection_success'),
        detail: t('success.connection_success_detail'),
        closable: false
      })
    } catch (error: any) {
      const errorDetail = error.response.data?.detail
      if (errorDetail) {
        apiError.value = t(`error.${errorDetail}`)
      } else {
        apiError.value = t(`error.network_issue`)
      }
      // toast affichant un message d'erreur
      toast.add({
        severity: 'error',
        life: 5000,
        summary: t('error.error'),
        detail: t('error.connection_failure'),
        closable: false
      })
    } finally {
      loading.value = false
    }
  }

  return { apiError, loading, onSubmit }
}

export default useLogin
