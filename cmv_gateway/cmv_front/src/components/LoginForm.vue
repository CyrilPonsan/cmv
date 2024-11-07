<script setup lang="ts">
/**
 * formulaire de connexion utilisateur
 * la logique est déplacée dans le composable "useLogin"
 */
import { Form, Field, type SubmissionHandler, type GenericObject } from 'vee-validate'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import useLogin from '@/composables/use-login'
import Password from 'primevue/password'
import Button from 'primevue/button'
import type { Credentials } from '@/models/credentials'

const { t } = useI18n()

const { error, initialValues, loginFormSchema, onSubmit } = useLogin()

const handleSubmit: SubmissionHandler<GenericObject> = (values) => {
  onSubmit(values as unknown as Credentials)
}
</script>

<template>
  <p>{{ error }}</p>
  <Form
    class="w-80 flex flex-col items-start gap-y-2"
    :validation-schema="loginFormSchema"
    :initial-values="initialValues"
    @submit="handleSubmit"
  >
    <!-- champs email -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="username">{{ t('login.labelEmail') }}</label>
      <!-- message d'erreur de validation du champs email -->
      <Field v-slot="{ field, errorMessage }" name="username">
        <Message class="text-xs" severity="error" v-show="errorMessage">{{ errorMessage }}</Message>
        <InputText
          fluid
          id="username"
          type="text"
          placeholder="jean.dupont@email.fr"
          v-bind="field"
          aria-label="adresse email"
          :invalid="!!errorMessage"
        />
      </Field>
    </div>
    <!-- champs mot de passe -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="password">{{ t('login.labelPassword') }}</label>
      <!-- message d'erreur de validation du champs mot de passe -->
      <Field v-slot="{ field, errorMessage }" name="password">
        <Message class="text-xs text-error" severity="error" v-show="errorMessage">{{
          errorMessage
        }}</Message>
        <Password
          fluid
          :modelValue="field.value"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          type="password"
          inputId="password"
          toggleMask
          :feedback="false"
          aria-label="password"
          :invalid="!!errorMessage"
        />
      </Field>
    </div>

    <!-- bouton pour soumettre le formulaire-->
    <div class="w-full flex justify-end m-2">
      <Button type="submit" label="Se Connecter" />
    </div>
    <Message v-if="error" :closable="true" :severity="'error'">{{
      t('error.connection_failure')
    }}</Message>
  </Form>
</template>
