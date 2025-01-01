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
  <div class="flex">
    <SidebarComponent />
    <div class="flex flex-col min-h-screen justify-between flex-1">
      <!--
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
                v-tooltip.bottom="t('app.tooltip.home')"
              />
              <li>
                <Button
                  :icon="colorSchemeIcon"
                  aria-label="theme"
                  text
                  rounded
                  v-tooltip.bottom="t('app.tooltip.change_mode')"
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
        -->
      <RouterView />
      <footer class="w-full h-16 flex justify-center items-center bg-black">
        <h3 class="text-xs text-primary-500">
          {{ t('app.footer') }}
        </h3>
      </footer>
    </div>
  </div>
</template>
