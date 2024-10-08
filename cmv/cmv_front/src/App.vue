<template>
  <header class="flex justify-end items-center p-2 bg-surface-900 h-[4rem]">
    <nav>
      <ul class="flex gap-x-2 items-center">
        <li>
          <Button
            :icon="colorSchemeIcon"
            aria-label="mode d'affichage"
            text
            @click="userStore.toggleColorScheme()"
          />
        </li>
        <li v-if="isLoggedIn">
          <Button icon="pi pi-sign-out" aria-label="déconnexion" text @click="userStore.logout()" />
        </li>
      </ul>
    </nav>
  </header>

  <RouterView />
</template>

<script setup lang="ts">
import { computed, onBeforeMount, watch } from 'vue'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'

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
