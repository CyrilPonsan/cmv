/**
 * Composable destiné à vérifier la validité des champs du formulaire.
 * Soumet les identifiants à l'API dans le but de connecter l'utilisateur.
 */
import { regexPassword } from '@/libs/regex'
import { useUserStore } from '@/stores/user'
import { toTypedSchema } from '@vee-validate/zod'
import { useToast } from 'primevue/usetoast'
import { watch, type Ref } from 'vue'
import { z } from 'zod'
import { useI18n } from 'vue-i18n'
import useHttp from './use-http'
import type { Credentials } from '@/models/credentials'

type LoginReturn = {
  error: Ref<string | null>
  initialValues: Credentials
  isLoading: Ref<boolean>
  loginFormSchema: ReturnType<typeof toTypedSchema>
  onSubmit: (values: Credentials) => void
}

/**
 * Hook personnalisé pour gérer la logique de connexion
 * @returns {LoginReturn} Objet contenant les fonctions et états nécessaires pour le formulaire de connexion
 */
const useLogin = (): LoginReturn => {
  // Initialisation des hooks et stores nécessaires
  const { t } = useI18n()
  const userStore = useUserStore()
  const { error, isLoading, sendRequest } = useHttp()
  const toast = useToast()

  // Valeurs initiales du formulaire
  const initialValues = {
    username: '',
    password: ''
  }

  /**
   * Schéma de validation Zod pour le formulaire de connexion
   * Vérifie que:
   * - username est un email valide
   * - password respecte le format requis (défini dans regexPassword)
   */
  const loginFormSchema = toTypedSchema(
    z.object({
      username: z
        .string({ required_error: t('error.no_email') })
        .email({ message: t('error.not_valid_email') }),
      password: z
        .string({ required_error: t('error.no_password') })
        .regex(regexPassword, { message: t('error.not_valid_password') })
    })
  )

  /**
   * Gère la soumission du formulaire
   * @param values - Les identifiants saisis par l'utilisateur
   */
  const onSubmit = (values: Credentials) => {
    /**
     * Callback appelé après une réponse réussie de l'API
     * @param data - Réponse de l'API contenant le statut et le message
     */
    const applyData = (data: { success: boolean; message: string }) => {
      if (data.success) {
        // Affiche un toast de succès et récupère les infos utilisateur
        toast.add({
          severity: 'success',
          life: 5000,
          summary: t('success.connection_success'),
          detail: t('success.connection_success_detail'),
          closable: false
        })
        userStore.getUserInfos()
      }
    }
    // Envoie la requête de connexion
    sendRequest({ path: '/auth/login', method: 'post', body: { ...values } }, applyData)
  }

  // Observe les erreurs pour afficher un toast en cas d'échec
  watch(error, (value) => {
    console.log('error', value)
    if (value && value.length > 0) {
      toast.add({
        severity: 'error',
        life: 5000,
        summary: t('error.error'),
        detail: t('error.connection_failure'),
        closable: false
      })
    }
  })

  // Retourne les fonctions et états nécessaires
  return {
    error,
    initialValues,
    isLoading,
    loginFormSchema,
    onSubmit
  }
}

export default useLogin
