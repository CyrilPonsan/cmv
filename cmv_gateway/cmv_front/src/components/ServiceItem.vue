<script setup lang="ts">
/**
 * @file ServiceItem.vue
 * @description Component for displaying a service
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */
import type Chambre from '@/models/chambre'
import ChambreItem from './ChambreItem.vue'
import Divider from 'primevue/divider'

interface Props {
  service: {
    id: number
    nom: string
    chambres: Chambre[]
  }
}

defineProps<Props>()
</script>

<template>
  <span class="w-full">
    <h2 class="text-xl font-bold">{{ service.nom }}</h2>
    <Divider />
    <div class="flex flex-wrap gap-4">
      <span v-for="chambre in service.chambres" v-bind:key="chambre.id">
        <ChambreItem v-bind:chambre="chambre" />
      </span>
    </div>
  </span>
</template>
