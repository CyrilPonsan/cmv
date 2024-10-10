<script setup lang="ts">
/**
 * formulaire de connexion utilisateur
 * la logique est déplacée dans le composable "useLogin"
 */
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Message from 'primevue/message'
import useLogin from '@/composables/use-login'

// ce composable gère la logique de validation et de connexion de l'utilisateur
const {
  apiError,
  errors,
  loading,
  password,
  passwordAttrs,
  passwordUpdate,
  username,
  usernameAttrs,
  onSubmit
} = useLogin()
</script>

<template>
  <main class="w-screen h-[70vh] flex flex-col justify-center items-center gap-8">
    <section>
      <h1 class="text-5xl font-bold">Clinique MONTVERT</h1>
    </section>
    <section class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <img
        class="w-96 h-96 hidden xl:block rounded-md shadow-sm"
        src="../assets/images/witch.jpg"
        alt="illustration page de connexion"
      />
      <article class="flex flex-col justify-center items-center gap-y-4">
        <form class="w-80 flex flex-col items-center gap-y-2" @submit.prevent="onSubmit">
          <!-- champs email -->
          <div class="w-full flex flex-col gap-y-2">
            <label for="username">Email</label>
            <!-- message d'erreur de validation du champs email -->
            <span class="flex items-center gap-x-2" v-show="errors.username">
              <Message
                severity="error"
                icon="pi pi-times-circle"
                aria-label="erreur adresse email"
              />
              <Message class="text-xs" severity="error">{{ errors.username }}</Message>
            </span>
            <InputText
              fluid
              id="username"
              type="email"
              name="username"
              placeholder="jean.dupont@email.fr"
              v-model="username"
              v-bind="usernameAttrs"
              aria-label="adresse email"
              :invalid="errors.username"
            />
          </div>
          <!-- champs mot de passe -->
          <div class="w-full flex flex-col gap-y-2">
            <label for="password">Mot de passe</label>
            <!-- message d'erreur de validation du champs mot de passe -->
            <span class="flex items-center gap-x-2" v-show="errors.password">
              <Message
                severity="error"
                icon="pi pi-times-circle"
                aria-label="erreur mot de passe"
              />
              <Message class="text-xs text-error" severity="error">{{ errors.password }}</Message>
            </span>
            <Password
              fluid
              v-model="password"
              v-bind="passwordAttrs"
              inputId="password"
              name="password"
              :feedback="false"
              toggleMask
              aria-label="password"
              :invalid="errors.password"
            />
          </div>

          <!-- bouton pour soumettre le formulaire-->
          <div class="flex justify-end mt-2">
            <Button type="submit" label="Se Connecter" :disabled="loading" :loading="loading" />
          </div>
        </form>
        <div>
          <Message class="text-xs" severity="error" v-show="apiError">{{ apiError }}</Message>
        </div>
        <pre>{{ passwordUpdate }}</pre>
      </article>
    </section>
  </main>
</template>
