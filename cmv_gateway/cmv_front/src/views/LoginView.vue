<script setup lang="ts">
/**
 * @file LoginView.vue
 * @description Login view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import LoginForm from '@/components/LoginForm.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <main class="w-screen h-[70vh] flex flex-col justify-center items-center gap-8 fade-in">
    <section>
      <h1 class="text-5xl text-primary-500 font-bold">{{ t('login.h1') }}</h1>
    </section>
    <section class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <img
        class="w-96 h-96 hidden xl:block rounded-md shadow-sm"
        src="../assets/images/docteur.webp"
        alt="illustration page de connexion"
      />
      <article class="flex flex-col justify-center items-center gap-y-4">
        <!-- formulaire de connexion -->
        <LoginForm />
      </article>
    </section>
  </main>
</template>

<style scoped>
.fade-in {
  opacity: 0;
  animation: fadeIn 2s ease-in-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
