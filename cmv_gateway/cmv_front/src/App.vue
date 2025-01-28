<script setup lang="ts">
/**
 * @file App.vue
 * @description Composant racine de l'application qui gère la navigation et l'authentification
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants Vue et des composables
import { computed, onBeforeMount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from './stores/user'
import { useRoute, useRouter } from 'vue-router'
import Toast from 'primevue/toast'
import SidebarComponent from './components/navigation/sidebar/SidebarComponent.vue'

// Initialisation des composables
const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// Computed property pour vérifier si l'utilisateur est connecté
const isLoggedIn = computed(() => userStore.role.length > 0)

// Surveillance des changements du rôle utilisateur pour la redirection
watch(
  () => userStore.role,
  (role) => {
    // Si l'utilisateur a été redirigé depuis une autre page
    if (route.redirectedFrom?.fullPath !== undefined && route.redirectedFrom?.fullPath !== '/') {
      router.push(route.redirectedFrom?.fullPath)
    }
    // Si l'utilisateur est connecté et sur la page racine
    else if (role.length > 0 && route.name === 'root') {
      switch (role) {
        case 'home':
          router.push({ name: 'patients' })
          break
        default:
          break
      }
    }
  }
)

// Vérification de l'authentification au chargement
onBeforeMount(() => {
  userStore.handshake()
})
</script>

<template>
  <!-- Composant Toast pour les notifications -->
  <Toast />
  <div class="flex relative">
    <!-- Barre latérale affichée uniquement si l'utilisateur est connecté -->
    <SidebarComponent v-if="isLoggedIn" />
    <div class="flex-1 flex flex-col min-h-screen justify-between">
      <!-- Router view pour afficher les différentes pages -->
      <RouterView />
      <!-- Pied de page -->
      <footer class="w-full h-16 flex justify-center items-center bg-black">
        <h3 class="text-xs text-primary-500">
          {{ t('app.footer') }}
        </h3>
      </footer>
    </div>
  </div>
</template>
