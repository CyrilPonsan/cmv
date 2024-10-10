/**
 * Composable destiné à vérifier la validité des champs du formulaire.
 * Soumet les identifiants à l'API dans le but de connecter l'utilisateur.
 */

import { regexPassword } from '@/libs/regex'
import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import { toTypedSchema } from '@vee-validate/zod'
import axios from 'axios'
import { useForm } from 'vee-validate'
import { ref } from 'vue'
import { z } from 'zod'

const useLogin = () => {
  const userStore = useUserStore()

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
  const { values, errors, defineField, handleSubmit } = useForm({
    validationSchema: loginFormSchema
  })

  // options pour le champs "email"
  const [username, usernameAttrs] = defineField('username', {
    validateOnModelUpdate: false
  })

  // options pour le champs "password"
  const [password, passwordAttrs] = defineField('password', {
    validateOnModelUpdate: false
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
      loading.value = false
    } catch (error: any) {
      console.error(error)
      loading.value = false
    }
  }

  // vérification de la validité des champs du formulaire
  const onSubmit = handleSubmit(() => {
    submitForm()
  })

  return {
    errors,
    loading,
    password,
    passwordAttrs,
    username,
    usernameAttrs,
    onSubmit
  }
}

export default useLogin
