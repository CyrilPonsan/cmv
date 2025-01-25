<script setup lang="ts">
import type Chambre from '@/models/chambre'
import Divider from 'primevue/divider'
import Card from 'primevue/card'
import { useI18n } from 'vue-i18n'
import { Button } from 'primevue'
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const { d, t } = useI18n()
const { role } = useUserStore()
const router = useRouter()

const { chambre } = defineProps<{ chambre: Chambre }>()

const statusColor = computed(() => {
  let style = 'flex justify-between items-center'
  switch (chambre.status) {
    case 'occupée':
      style += ' text-red-500'
      break
    case 'libre':
      style += ' text-green-500'
      break
    default:
      style += ' text-orange-500'
  }
  return style
})

const goToPatientDetails = () => {
  router.push(`/patient/${chambre.reservations[0].patient.id_patient}`)
}
</script>

<template>
  <Card class="w-96" style="overflow: hidden">
    <template #title>
      <div :class="statusColor">
        <p class="capitalize">{{ chambre.nom }}</p>
        <p class="capitalize">{{ t(`components.chambre.${chambre.status}`) }}</p>
      </div>
      <Divider />
    </template>
    <template #content>
      <div class="flex flex-col mt-4">
        <span class="capitalize" v-if="chambre.status === 'occupée'">
          {{ t('components.chambre.occupant') }}
          {{
            chambre.reservations && chambre.reservations.length > 0
              ? chambre.reservations[0].patient.full_name
              : ''
          }}</span
        >
        <span
          v-if="
            role && role !== 'cleaner' && chambre.reservations && chambre.reservations.length > 0
          "
        >
          {{ t('components.chambre.sortie_prevue') }} :
          {{ d(new Date(chambre.reservations[0].sortie_prevue), 'short') }}
        </span>
        <span>
          {{ t('components.chambre.dernier_nettoyage') }} :
          {{ d(new Date(chambre.dernier_nettoyage), 'short') }}
        </span>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end items-center">
        <Button
          variant="text"
          icon="pi pi-user"
          :disabled="chambre.status !== 'occupée'"
          :aria-label="t('components.chambre.voir_details')"
          v-tooltip.bottom="t('components.chambre.voir_details')"
          @click="goToPatientDetails"
        />
      </div>
    </template>
  </Card>
</template>
