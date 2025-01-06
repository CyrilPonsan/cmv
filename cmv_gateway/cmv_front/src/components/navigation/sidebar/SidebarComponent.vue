<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import Button from 'primevue/button'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const userStore = useUserStore()
const { t } = useI18n()

const colorSchemeIcon = computed(() => `pi pi-${userStore.mode === 'dark' ? 'moon' : 'sun'}`)
</script>

<template>
  <div class="w-64 sticky top-0 left-0 h-screen bg-surface-900 flex flex-col justify-between">
    <span>
      <img class="w-48 h-auto" src="@/assets/images/cmv-logo.webp" alt="logo" />
    </span>

    <span class="flex-1 flex flex-col justify-evenly items-center">
      <ul class="w-full p-4 flex flex-col gap-y-4">
        <li>
          <Button class="w-full" as="router-link" :label="t('app.sidebar.home')" to="/" />
        </li>
        <li>
          <Button class="w-full" as="router-link" :label="t('app.sidebar.rooms')" to="/chambres" />
        </li>
      </ul>
    </span>

    <span>
      <ul class="flex justify-center items-center gap-x-2 p-2">
        <Button
          :icon="colorSchemeIcon"
          aria-label="theme"
          text
          rounded
          v-tooltip.right="t('app.tooltip.change_mode')"
          @click="userStore.toggleColorScheme()"
        />
        <Button
          icon="pi pi-sign-out"
          aria-label="déconnexion"
          text
          rounded
          v-tooltip.right="t('app.tooltip.logout')"
          @click="userStore.signout()"
        />
      </ul>
    </span>
  </div>
</template>
