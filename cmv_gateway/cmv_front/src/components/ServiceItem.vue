<script setup lang="ts">
/**
 * @file ServiceItem.vue
 * @description Component for displaying a service
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import ChambreItem from './ChambreItem.vue'
import Divider from 'primevue/divider'
import type Service from '@/models/service'

const service = defineProps<Service>()
</script>

<template>
  <span class="w-full">
    <h2 class="text-xl font-bold">{{ service.nom }}</h2>
    <Divider />
    <div class="flex flex-wrap gap-4">
      <span v-for="chambre in service.chambres" v-bind:key="chambre.id_chambre">
        <ChambreItem v-bind:chambre="chambre" />
      </span>
    </div>
  </span>
</template>
