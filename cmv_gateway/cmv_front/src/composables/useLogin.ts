/**
 * @file use-login.ts
 * @description Composable pour gérer la logique de connexion utilisateur
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import { regexPassword } from '@/libs/regex' // Regex pour la validation du mot de passe
import { useUserStore } from '@/stores/user' // Store Pinia pour la gestion de l'utilisateur
import { toTypedSchema } from '@vee-validate/zod' // Utilitaire pour convertir un schéma Zod en schéma VeeValidate
import { useToast } from 'primevue/usetoast' // Hook PrimeVue pour afficher des notifications
import { watch, type Ref } from 'vue' // Fonctionnalités Vue.js
import { z } from 'zod' // Bibliothèque de validation
import { useI18n } from 'vue-i18n' // Hook pour l'internationalisation
import useHttp from './useHttp' // Hook personnalisé pour les requêtes HTTP
import type { Credentials } from '@/models/credentials' // Type pour les identifiants

/**
 * Type définissant les valeurs retournées par le composable useLogin
 */
type LoginReturn = {
  error: Ref<string | null> // Message d'erreur éventuel
  initialValues: Credentials // Valeurs initiales du formulaire
  isLoading: Ref<boolean> // État de chargement
  loginFormSchema: ReturnType<typeof toTypedSchema> // Schéma de validation du formulaire
  onSubmit: (values: Credentials) => void // Fonction de soumission du formulaire
}

/**
 * Composable pour gérer la logique de connexion
 * @returns {LoginReturn} Objet contenant les fonctions et états nécessaires pour le formulaire de connexion
 */
const useLogin = (): LoginReturn => {
  // Initialisation des hooks et stores nécessaires
  const { t } = useI18n() // Hook pour les traductions
  const userStore = useUserStore() // Store utilisateur
  const { error, isLoading, sendRequest } = useHttp() // Hook pour les requêtes HTTP
  const toast = useToast() // Hook pour les notifications

  // Valeurs initiales du formulaire de connexion
  const initialValues = {
    username: '',
    password: ''
  }

  /**
   * Schéma de validation du formulaire utilisant Zod
   * Vérifie que l'email est valide et que le mot de passe respecte le format requis
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
   * Gère la soumission du formulaire de connexion
   * @param values - Les identifiants saisis par l'utilisateur
   */
  const onSubmit = (values: Credentials) => {
    /**
     * Callback appelé après une réponse réussie de l'API
     * @param data - Réponse de l'API contenant le statut et le message
     */
    const applyData = (data: { success: boolean; message: string }) => {
      if (data.success) {
        // Affiche une notification de succès et récupère les informations utilisateur
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
    // Envoie la requête de connexion à l'API
    sendRequest({ path: '/auth/login', method: 'post', body: { ...values } }, applyData)
  }

  /**
   * Observe les changements d'état de l'erreur
   * Affiche une notification en cas d'erreur de connexion
   */
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

  // Retourne l'interface publique du composable
  return {
    error,
    initialValues,
    isLoading,
    loginFormSchema,
    onSubmit
  }
}

export default useLogin
