<template>
  <Button icon="pi pi-sun" text @click="userStore.toggleColorScheme()" />

  <RouterView />
</template>

<script setup lang="ts">
import { onBeforeMount, watch } from 'vue'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'

const router = useRouter()
const route = useRoute()

const userStore = useUserStore()

watch(
  () => userStore.role,
  (role) => {
    if (route.redirectedFrom?.fullPath !== undefined && route.redirectedFrom?.fullPath !== '/') {
      router.push(route.redirectedFrom?.fullPath)
    } else if (role.length > 0)
      switch (role) {
        case 'nurses':
          router.push({ name: 'chambres' })
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
