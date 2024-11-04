<script setup lang="ts">
/**
 * formulaire de connexion utilisateur
 * la logique est déplacée dans le composable "useLogin"
 */
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Message from 'primevue/message'
import { useI18n } from 'vue-i18n'
import useGenericForm from '@/composables/use-generic-form'
import { toTypedSchema } from '@vee-validate/zod'
import { useUserStore } from '@/stores/user'
import { regexPassword } from '@/libs/regex'
import { AUTH } from '@/libs/urls'
import { z } from 'zod'

const { t } = useI18n()
const userStore = useUserStore()

// schema de validation utilisé pour le formulaire de connexion
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

// ce composable gère la logique de validation et de connexion de l'utilisateur
const form = useGenericForm({
  schema: loginFormSchema,
  submitEndpoint: `${AUTH}/auth/login`,
  onSuccess: () => userStore.getUserInfos(),
  successMessage: {
    summary: t('success.connection_success'),
    detail: t('success.connection_success_detail')
  }
})
</script>
<template>
  <form class="w-80 flex flex-col items-center gap-y-2" @submit.prevent="form.onSubmit">
    <!-- champs email -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="username">{{ t('login.labelEmail') }}</label>
      <!-- message d'erreur de validation du champs email -->
      <span class="flex items-center gap-x-2" v-show="form.errors.username">
        <Message severity="error" icon="pi pi-times-circle" aria-label="erreur adresse email" />
        <Message class="text-xs" severity="error">{{ form.errors.username }}</Message>
      </span>
      <InputText
        fluid
        id="username"
        type="email"
        name="username"
        placeholder="jean.dupont@email.fr"
        v-model="form.fields.username.value"
        v-bind="form.fields.username.attrs"
        aria-label="adresse email"
        :invalid="form.errors.username"
      />
    </div>
    <!-- champs mot de passe -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="password">{{ t('login.labelPassword') }}</label>
      <!-- message d'erreur de validation du champs mot de passe -->
      <span class="flex items-center gap-x-2" v-show="form.errors.password">
        <Message severity="error" icon="pi pi-times-circle" aria-label="erreur mot de passe" />
        <Message class="text-xs text-error" severity="error">{{ form.errors.password }}</Message>
      </span>
      <Password
        fluid
        v-model="form.fields.password.value"
        v-bind="form.fields.password.attrs"
        inputId="password"
        name="password"
        :feedback="false"
        toggleMask
        aria-label="password"
        :invalid="form.errors.password"
      />
    </div>

    <!-- bouton pour soumettre le formulaire-->
    <div class="flex justify-end mt-2">
      <Button type="submit" label="Se Connecter" :disabled="form.loading" :loading="form.loading" />
    </div>
  </form>
  <div>
    <Message class="text-xs" severity="error" v-show="form.apiError">{{ form.apiError }}</Message>
  </div>
</template>
