<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<template>
  <div class="w-80 h-64 rounded-xl shadow-lg border border-secondary/20">
    <span :class="style"
      ><p>{{ chambre.numero }}</p>
      <p>{{ chambre.status }}</p></span
    >
    <div class="p-4 text-sm">
      <p>{{ chambre.status }}</p>
      <p>{{ chambre.last_freed }}</p>
      <p>{{ chambre.last_occuped }}</p>
      <p>{{ chambre.last_cleanup }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type Chambre from '@/models/chambre'
import { computed } from 'vue'

interface Props {
  chambre: Chambre
}

const props = defineProps<Props>()

const style = computed(() => {
  const baseStyle =
    'text-xl font-bold p-4 rounded-tl-xl rounded-tr-xl flex justify-between text-neutral-content w-full'
  switch (props.chambre.status) {
    case 'occupée':
      return baseStyle + ' bg-primary'
    default:
      return baseStyle + ' bg-secondary'
  }
})
</script>
