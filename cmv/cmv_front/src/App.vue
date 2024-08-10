<template>
  <Button label="Toggle Color Scheme" @click="toggleColorScheme()" />

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

const toggleColorScheme = () => {
  const element = document.querySelector('html')

  if (element) element.classList.toggle('my-app-dark')

  if (element && element.classList && element.classList.value === 'my-app-dark')
    console.log('hello darkness my friend')

  console.log(element?.classList)
}

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
