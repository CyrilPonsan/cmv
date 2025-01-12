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
  <div
    class="w-64 sticky top-0 left-0 h-screen bg-surface-900 flex flex-col justify-between items-center"
  >
    <span>
      <img class="w-full h-auto" src="@/assets/images/cmv-logo.jpeg" alt="logo" />
    </span>

    <span class="flex-1 flex flex-col justify-evenly items-center">
      <ul class="w-full p-2 flex flex-col gap-y-4">
        <li>
          <Button
            class="w-full"
            as="router-link"
            severity="secondary"
            :label="t('app.sidebar.home')"
            to="/"
          />
        </li>
        <li>
          <Button
            class="w-full"
            as="router-link"
            severity="secondary"
            :label="t('app.sidebar.rooms')"
            to="/chambres"
          />
        </li>
        <li>
          <Button
            class="w-full"
            as="a"
            severity="secondary"
            label="Rendez-vous"
            href="https://www.doctissimo.fr/"
            target="_blank"
          />
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
