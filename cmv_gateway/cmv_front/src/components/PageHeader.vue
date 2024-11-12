<script setup lang="ts">
/**
 * @file PageHeader.vue
 * @description Component for displaying the page header
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Props du composant
const { description, title } = defineProps<{
  description: string // Description de la page
  title: string // Titre de la page
}>()
</script>

<template>
  <!-- Container principal avec espacement vertical -->
  <div class="flex flex-col gap-y-2">
    <!-- Titre principal de la page -->
    <h1 class="text-3xl font-bold">{{ title }}</h1>

    <!-- Sous-titre / Description de la page -->
    <h2 class="text-sm text-neutral-500/50 font-bold">{{ description }}</h2>
  </div>
</template>
