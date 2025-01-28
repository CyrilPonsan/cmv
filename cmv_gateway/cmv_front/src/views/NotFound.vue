<script setup lang="ts">
import Button from 'primevue/button'
</script>

<template>
  <section class="h-screen flex flex-col justify-center items-center gap-y-4">
    <h1 class="text-3xl font-bold">Erreur 404 : La page n'existe pas.</h1>
    <Button as="router-link" to="/" label="Retour à l'accueil" variant="text" />
  </section>
</template>
