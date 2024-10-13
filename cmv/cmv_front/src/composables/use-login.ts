/**
 * Composable destiné à vérifier la validité des champs du formulaire.
 * Soumet les identifiants à l'API dans le but de connecter l'utilisateur.
 */
import { regexPassword } from '@/libs/regex'
import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import { toTypedSchema } from '@vee-validate/zod'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import { useForm } from 'vee-validate'
import { ref, watch, watchEffect } from 'vue'
import { z } from 'zod'

const useLogin = () => {
  const userStore = useUserStore()
  const toast = useToast()
  const apiError = ref('')

  const usernameUpdate = ref(false)
  const passwordUpdate = ref(false)

  // schema de validation utilisé pour le formulaire de connexion
  const loginFormSchema = toTypedSchema(
    z.object({
      username: z.string({ required_error: 'no_email' }).email({ message: 'not_valid_email' }),
      password: z
        .string({ required_error: 'no_password' })
        .regex(regexPassword, { message: 'not_valid_password' })
    })
  )

  // configuration de la validation du formulaire
  const { values, errors, handleSubmit, defineField, validateField } = useForm({
    validationSchema: loginFormSchema
  })

  // options pour le champs "email"
  const [username, usernameAttrs] = defineField('username', {
    validateOnModelUpdate: false
  })

  // options pour le champs "password"
  const [password, passwordAttrs] = defineField('password', {
    validateOnChange: passwordUpdate.value,
    validateOnModelUpdate: passwordUpdate.value
  })

  // Surveille les changements de valeur de l'identifiant et force sa validation si une erreur a déjà été détecté
  watch(username, async () => {
    if (usernameUpdate.value) {
      // valide manuellement le champ "password"
      await validateField('username')
    }
  })

  // Surveille les changements de valeur du mot de passe et force la validation du champ mot de passe si une erreur a déjà été détecté
  watch(password, async () => {
    if (passwordUpdate.value) {
      // valide manuellement le champ "password"
      await validateField('password')
    }
  })

  // état du loader
  const loading = ref(false)

  // requête http pour connecter l'utilisateur
  const submitForm = async () => {
    loading.value = true
    try {
      await axios.post(`${AUTH}/auth/login`, {
        username: values.username,
        password: values.password
      })
      userStore.getUserInfos()
      // affiche un toast attestant du succès de la connexion
      toast.add({
        severity: 'success',
        life: 5000,
        summary: 'Connexion réussie',
        detail: 'Bienvenue copain !',
        contentStyleClass: 'color: red',
        closable: false
      })
    } catch (error: any) {
      apiError.value = error.response.data.detail ?? error.response.data
      // toast affichant un message d'erreur
      toast.add({
        severity: 'error',
        life: 5000,
        summary: 'Error spotted',
        detail: 'La connexion a échouée...',
        contentStyleClass: 'color: red',
        closable: false
      })
    } finally {
      loading.value = false
    }
  }

  // vérification de la validité des champs du formulaire
  const onSubmit = handleSubmit(() => {
    submitForm()
  })

  watchEffect(() => {
    if (errors.value.password) {
      console.log('updating...')
      passwordUpdate.value = true
    }
  })

  watchEffect(() => {
    if (errors.value.username) {
      usernameUpdate.value = true
    }
  })

  return {
    apiError,
    errors,
    loading,
    password,
    passwordAttrs,
    passwordUpdate,
    username,
    usernameAttrs,
    onSubmit
  }
}

export default useLogin
