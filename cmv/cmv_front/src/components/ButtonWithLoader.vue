<template>
  <button class="btn btn-primary" v-bind:disabled="loading">
    <div class="flex gap-x-2 items-center">
      <IconLoader class="animate-spin" v-if="loading" />
      <p v-if="loading">{{ loadingLabel }}</p>
      <p v-else>{{ label }}</p>
    </div>
  </button>
</template>

<script setup lang="ts">
import IconLoader from './icons/IconLoader.vue'

interface Props {
  label: string
  loadingLabel: string
  loading: boolean
}

const { label, loadingLabel, loading } = defineProps<Props>()
</script>
