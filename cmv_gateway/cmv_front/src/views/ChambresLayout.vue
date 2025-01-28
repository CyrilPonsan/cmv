<script setup lang="ts">
/**
 * @file ChambresLayout.vue
 * @description Layout pour la gestion des chambres
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import du composant RouterView pour le routage
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- Container principal avec une largeur minimale, une hauteur minimale et du padding -->
  <main class="min-w-screen min-h-[80vh] p-[2rem]">
    <!-- Affichage des vues enfants via RouterView -->
    <RouterView />
  </main>
</template>
