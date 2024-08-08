<script setup lang="ts">
import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const userStore = useUserStore()

const form = {
  email: '',
  password: ''
}

const submitForm = async () => {
  const formData = new FormData()
  formData.append('username', form.email)
  formData.append('password', form.password)
  try {
    const response = await axios.post(`${AUTH}/auth/login`, formData)
    userStore.setTokens(response.data)

    userStore.handshake()
  } catch (error: any) {
    console.error(error)
  }
}
</script>

<template>
  <main class="flex justify-center items-center">
    <form class="flex flex-col gap-y-2" v-on:submit.prevent="submitForm">
      <div class="flex flex-col gap-y-2">
        <label for="email">Email</label>
        <input
          class="input input-bordered"
          type="email"
          placeholder="jean.dupont@email.fr"
          v-model="form.email"
        />
      </div>
      <div class="flex flex-col gap-y-2">
        <label for="email">Mot de passe</label>
        <input class="input input-bordered" type="password" v-model="form.password" />
      </div>
      <div class="flex justify-end mt-2">
        <button class="btn btn-primary">Envoyer</button>
      </div>
    </form>
  </main>
</template>
