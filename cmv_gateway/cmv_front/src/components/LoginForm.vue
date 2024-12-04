<script setup lang="ts">
/**
 * @file LoginForm.vue
 * @description Component for the login form
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import { Form, Field, type SubmissionHandler, type GenericObject } from 'vee-validate' // Validation de formulaire
import { useI18n } from 'vue-i18n' // Internationalisation
import InputText from 'primevue/inputtext' // Champ de texte PrimeVue
import Message from 'primevue/message' // Message d'erreur PrimeVue
import useLogin from '@/composables/useLogin' // Hook personnalisé pour la logique de connexion
import Password from 'primevue/password' // Champ mot de passe PrimeVue
import Button from 'primevue/button' // Bouton PrimeVue
import type { Credentials } from '@/models/credentials' // Type pour les identifiants

// Récupération des fonctions d'internationalisation
const { t } = useI18n()

// Récupération des fonctionnalités du hook de connexion
const { error, initialValues, isLoading, loginFormSchema, onSubmit } = useLogin()

/**
 * Gère la soumission du formulaire
 * @param values Les valeurs du formulaire
 */
const handleSubmit: SubmissionHandler<GenericObject> = (values) => {
  onSubmit(values as unknown as Credentials)
}
</script>

<template>
  <!-- Formulaire de connexion -->
  <Form
    class="w-80 flex flex-col items-start gap-y-2"
    :validation-schema="loginFormSchema"
    :initial-values="initialValues"
    @submit="handleSubmit"
  >
    <!-- Champ email -->
    <div class="w-full flex flex-col gap-y-2">
      <!-- Message d'erreur de validation du champ email -->
      <Field v-slot="{ field, errorMessage }" name="username">
        <label for="username">{{ t('login.labelEmail') }}</label>
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

    <!-- Champ mot de passe -->
    <div class="w-full flex flex-col gap-y-2">
      <label for="password">{{ t('login.labelPassword') }}</label>
      <!-- Message d'erreur de validation du champ mot de passe -->
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

    <!-- Bouton de soumission -->
    <div class="w-full flex justify-end m-2">
      <Button type="submit" label="Se Connecter" :loading="isLoading" />
    </div>

    <!-- Message d'erreur de connexion -->
    <Message v-if="error" class="w-full" :closable="true" :severity="'error'">{{
      t(`error.${error}`)
    }}</Message>
  </Form>
</template>
