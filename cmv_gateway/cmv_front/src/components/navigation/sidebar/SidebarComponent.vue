<script setup lang="ts">
// Import des composants et stores nécessaires
import { useUserStore } from '@/stores/user'
import SidebarAccueil from '@/components/navigation/sidebar/SidebarAccueil.vue'
import SidebarFooter from '@/components/navigation/sidebar/SidebarFooter.vue'

// Récupération du store utilisateur
const userStore = useUserStore()
</script>

<template>
  <!-- Conteneur principal de la sidebar -->
  <main
    class="w-48 sticky top-0 left-0 h-screen bg-surface-900 flex flex-col justify-between items-center"
  >
    <!-- Section logo -->
    <section>
      <img
        class="rounded-lg shadow-lg p-2 mt-8 h-36 w-36"
          src="@/assets/images/logo.png"
          width="144"
          height="144"
        alt="logo de la clinique"
      />
    </section>

    <!-- Section menu du service accueil (visible uniquement pour le rôle 'home') -->
    <section v-if="userStore.role === 'home'">
      <SidebarAccueil />
    </section>

    <!-- Section footer avec boutons de thème et déconnexion -->
    <section>
      <SidebarFooter />
    </section>
  </main>
</template>
