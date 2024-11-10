<script setup lang="ts">
import { computed, onBeforeMount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Toast from 'primevue/toast'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const colorSchemeIcon = computed(() => `pi pi-${userStore.mode === 'dark' ? 'moon' : 'sun'}`)

const isLoggedIn = computed(() => userStore.role.length > 0)

watch(
  () => userStore.role,
  (role) => {
    if (route.redirectedFrom?.fullPath !== undefined && route.redirectedFrom?.fullPath !== '/') {
      router.push(route.redirectedFrom?.fullPath)
    } else if (role.length > 0)
      switch (role) {
        case 'home':
          router.push({ name: 'patients' })
          break
        default:
          break
      }
  }
)

onBeforeMount(() => {
  userStore.handshake()
})
</script>

<template>
  <Toast />
  <main class="min-h-screen flex flex-col justify-between">
    <span>
      <header class="flex justify-end items-center p-2 bg-surface-900 h-[4rem]">
        <nav>
          <ul class="flex gap-x-2 items-center">
            <Button
              as="router-link"
              to="/"
              icon="pi pi-home"
              aria-label="redirection vers l'accueil"
              size="small"
              text
              rounded
              v-tooltip.left="t('app.tooltip.home')"
            />
            <li>
              <Button
                :icon="colorSchemeIcon"
                aria-label="theme"
                text
                rounded
                v-tooltip.left="t('app.tooltip.change_mode')"
                @click="userStore.toggleColorScheme()"
              />
            </li>
            <li v-if="isLoggedIn">
              <Button
                icon="pi pi-sign-out"
                aria-label="déconnexion"
                text
                rounded
                v-tooltip.left="t('app.tooltip.logout')"
                @click="userStore.signout()"
              />
            </li>
          </ul>
        </nav>
      </header>
      <RouterView />
    </span>

    <footer class="w-full h-[4rem] flex justify-center items-center bg-surface-900">
      <h3 class="text-xs text-primary-500">
        {{ t('app.footer') }}
      </h3>
    </footer>
  </main>
</template>
