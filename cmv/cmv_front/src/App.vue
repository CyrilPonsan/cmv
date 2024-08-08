<template>
  <main class="min-w-screen min-h-screen flex justify-center items-center">
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { onBeforeMount, watch } from 'vue'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'

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
