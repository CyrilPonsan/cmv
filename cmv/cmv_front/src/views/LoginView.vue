<script setup lang="ts">
import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { reactive, ref } from 'vue'
import { boolean, string, z } from 'zod'
import { regexPassword } from '@/libs/regex'
import Message from 'primevue/message'
import type ValidationError from '@/models/validation-error'

const userStore = useUserStore()

/**
 * schema de validation utilisé pour le formulaire de connexion
 *
 */
const loginFormSchema = z.object({
  username: z.string({ required_error: 'no_email' }).email({ message: 'not_valid_email' }),
  password: z
    .string({ required_error: 'no_password' })
    .regex(regexPassword, { message: 'not_valid_password' })
})

const validationErrors: ValidationError[] = []

const loginFormValues = reactive({
  username: '',
  password: '',
  usernameIsValid: true,
  passwordIsValid: true
})

/*
const username = ref('')
const password = ref('')
const mailIsValid = ref(true)
const passwordIsValid = ref(true)
*/

const loading = ref(false)

const submitForm = async () => {
  loading.value = true
  try {
    await axios.post(`${AUTH}/auth/login`, {
      username: loginFormValues.username,
      password: loginFormValues.password
    })
    userStore.getUserInfos()
    loading.value = false
  } catch (error: any) {
    console.error(error)
    loading.value = false
  }
}
const handleEmailChange = (event: Event) => {
  console.log((event.target as HTMLInputElement).value)
}
</script>

<template>
  <main class="flex justify-center items-center">
    <form class="flex flex-col gap-y-2" v-on:submit.prevent="submitForm">
      <div class="flex flex-col gap-y-2">
        <label for="email">Email</label>
        <span class="flex items-center gap-x-2">
          <InputText
            type="email"
            placeholder="jean.dupont@email.fr"
            v-model="loginFormValues.username"
            @change="handleEmailChange"
          />
          <Message
            v-show="!loginFormValues.usernameIsValid"
            severity="error"
            icon="pi pi-times-circle"
          />
        </span>
      </div>
      <div class="flex flex-col gap-y-2">
        <label for="email">Mot de passe</label>
        <Password v-model="loginFormValues.password" :feedback="false" toggleMask />
      </div>
      <div class="flex justify-end mt-2">
        <Button type="submit" label="Se Connecter" :disabled="loading" :loading="loading" />
      </div>
    </form>
  </main>
</template>
