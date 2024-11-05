<script setup lang="ts">
/**
 * formulaire de connexion utilisateur
 * la logique est déplacée dans le composable "useLogin"
 */
import { Form, Field } from 'vee-validate'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import useLogin from '@/composables/use-login'
import Password from 'primevue/password'
import Button from 'primevue/button'

const { t } = useI18n()

const { onSubmit, initialValues, loginFormSchema } = useLogin()

const handleSubmit = (values: any) => {
  onSubmit(values)
}
</script>
<template>
  <Form
    class="w-80 flex flex-col items-center gap-y-2"
    :validation-schema="loginFormSchema"
    :initial-values="initialValues"
    @submit="handleSubmit"
  >
    <!-- champs email -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="username">{{ t('login.labelEmail') }}</label>
      <!-- message d'erreur de validation du champs email -->
      <Field v-slot="{ field, errorMessage }" name="username">
        <span class="flex items-center gap-x-2" v-show="errorMessage">
          <Message severity="error" icon="pi pi-times-circle" aria-label="erreur adresse email" />
          <Message class="text-xs" severity="error">{{ errorMessage }}</Message>
        </span>
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
        <span class="flex items-center gap-x-2" v-show="errorMessage">
          <Message severity="error" icon="pi pi-times-circle" aria-label="erreur mot de passe" />
          <Message class="text-xs text-error" severity="error">{{ errorMessage }}</Message>
        </span>
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
    <div class="flex justify-end mt-2">
      <Button type="submit" label="Se Connecter" />
    </div>
  </Form>
  <div></div>
</template>
