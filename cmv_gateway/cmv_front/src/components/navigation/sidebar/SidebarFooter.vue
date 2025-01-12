<script setup lang="ts">
// Import des stores et composants nécessaires
import { useUserStore } from '@/stores/user'
import { Button } from 'primevue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

// Initialisation des stores
const userStore = useUserStore()
const { t } = useI18n()

// Computed property pour l'icône du thème (soleil/lune)
const colorSchemeIcon = computed(() => `pi pi-${userStore.mode === 'dark' ? 'moon' : 'sun'}`)
</script>

<template>
  <!-- Liste des boutons du footer -->
  <ul class="flex justify-center items-center gap-x-2 p-2">
    <!-- Bouton de changement de thème -->
    <Button
      :icon="colorSchemeIcon"
      aria-label="theme"
      text
      rounded
      v-tooltip.right="t('app.tooltip.change_mode')"
      @click="userStore.toggleColorScheme()"
    />
    <!-- Bouton de déconnexion -->
    <Button
      icon="pi pi-sign-out"
      aria-label="déconnexion"
      text
      rounded
      v-tooltip.right="t('app.tooltip.logout')"
      @click="userStore.signout()"
    />
  </ul>
</template>
