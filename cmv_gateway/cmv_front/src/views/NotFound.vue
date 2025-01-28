<script setup lang="ts">
/**
 * @file NotFound.vue
 * @description Page d'erreur 404 affichée lorsqu'une route n'existe pas
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import du composant Button de PrimeVue
import Button from 'primevue/button'
</script>

<template>
  <!-- Container principal centré verticalement et horizontalement -->
  <section class="h-screen flex flex-col justify-center items-center gap-y-4">
    <!-- Message d'erreur 404 -->
    <h1 class="text-3xl font-bold">Erreur 404 : La page n'existe pas.</h1>
    <!-- Bouton de retour à l'accueil utilisant le composant router-link -->
    <Button as="router-link" to="/" label="Retour à l'accueil" variant="text" />
  </section>
</template>
