<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<template>
  <Card class="w-96" style="overflow: hidden">
    <template #title>
      <div class="text-green-500 flex justify-between items-center">
        <p class="capitalize">{{ chambre.nom }}</p>
        <p class="capitalize">{{ chambre.status }}</p>
      </div>
      <Divider />
    </template>
    <template #content>
      <div class="flex flex-col gap-y-2 mt-4">
        <span>Dernier nettoyage : {{ d(new Date(chambre.dernier_nettoyage), 'short') }}</span>
        <span>
          {{
            chambre.reservation && chambre.reservation.length > 0
              ? chambre.reservation[0].patient.full_name
              : ''
          }}</span
        >
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end items-center">
        <Button
          variant="text"
          icon="pi pi-user"
          :disabled="chambre.status !== 'occupée'"
          aria-label="Voir les détails de l'occupant"
          v-tooltip.bottom="'Voir les détails du patient'"
        />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import type Chambre from '@/models/chambre'
import Divider from 'primevue/divider'
import Card from 'primevue/card'
import { useI18n } from 'vue-i18n'
import { Button } from 'primevue'

const { d } = useI18n()

const { chambre } = defineProps<{ chambre: Chambre }>()
</script>
