<script setup lang="ts">
import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { ref } from 'vue'

const userStore = useUserStore()

const username = ref('')
const password = ref('')

const loading = ref(false)

const submitForm = async () => {
  loading.value = true
  try {
    await axios.post(`${AUTH}/auth/login`, {
      username: username.value,
      password: password.value
    })
    userStore.getUserInfos()
    loading.value = false
  } catch (error: any) {
    console.error(error)
    loading.value = false
  }
}
</script>

<template>
  <main class="flex justify-center items-center">
    <form class="flex flex-col gap-y-2" v-on:submit.prevent="submitForm">
      <div class="flex flex-col gap-y-2">
        <label for="email">Email</label>
        <InputText type="email" placeholder="jean.dupont@email.fr" v-model="username" />
      </div>
      <div class="flex flex-col gap-y-2">
        <label for="email">Mot de passe</label>
        <Password v-model="password" :feedback="false" toggleMask />
      </div>
      <div class="flex justify-end mt-2">
        <Button type="submit" label="Se Connecter" :disabled="loading" :loading="loading" />
      </div>
    </form>
  </main>
</template>
