<template>
  <span class="w-full">
    <h2 class="text-xl font-bold">{{ service.nom }}</h2>
    <div class="divider" />
    <div class="flex flex-wrap gap-4">
      <span v-for="chambre in service.chambres" v-bind:key="chambre.id">
        <ChambreItem v-bind:chambre="chambre" />
      </span>
    </div>
  </span>
</template>

<script setup lang="ts">
import type Chambre from '@/models/chambre'
import ChambreItem from './ChambreItem.vue'

interface Props {
  service: {
    id: number
    nom: string
    chambres: Chambre[]
  }
}

defineProps<Props>()
</script>
