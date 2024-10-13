<script setup lang="ts">
const { description, title } = defineProps<{
  description: string
  title: string
}>()
</script>

<template>
  <div class="flex flex-col gap-y-2">
    <h1 class="text-3xl font-bold">{{ title }}</h1>
    <h2 class="text-sm text-neutral-500/50 font-bold">{{ description }}</h2>
  </div>
</template>
