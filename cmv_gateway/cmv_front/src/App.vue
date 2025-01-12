<script setup lang="ts">
import { computed, onBeforeMount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'
import Toast from 'primevue/toast'
import SidebarComponent from './components/navigation/sidebar/SidebarComponent.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

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
  <div class="flex relative">
    <SidebarComponent v-if="isLoggedIn" />
    <div class="w-full flex flex-col min-h-screen justify-between">
      <RouterView />
      <footer class="w-full h-16 flex justify-center items-center bg-black">
        <h3 class="text-xs text-primary-500">
          {{ t('app.footer') }}
        </h3>
      </footer>
    </div>
  </div>
</template>
