<script setup lang="ts">
// Importation des composants et types nécessaires
import type Chambre from '@/models/chambre'
import Divider from 'primevue/divider'
import Card from 'primevue/card'
import { useI18n } from 'vue-i18n'
import { Button } from 'primevue'
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

// Initialisation des hooks
const { d, t } = useI18n()
const { role } = useUserStore()
const router = useRouter()

// Définition des props du composant
const { chambre } = defineProps<{ chambre: Chambre }>()

// Calcul de la couleur du statut en fonction de l'état de la chambre
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

// Fonction de navigation vers les détails du patient
const goToPatientDetails = () => {
  router.push(`/patient/${chambre.reservations[0].patient.ref_patient}`)
}
</script>

<template>
  <!-- Carte principale affichant les informations de la chambre -->
  <Card class="w-96" style="overflow: hidden">
    <!-- En-tête de la carte avec le nom et le statut de la chambre -->
    <template #title>
      <div :class="statusColor">
        <p class="capitalize">{{ chambre.nom }}</p>
        <p class="capitalize">{{ t(`components.chambre.${chambre.status}`) }}</p>
      </div>
      <Divider />
    </template>
    <!-- Contenu principal de la carte -->
    <template #content>
      <div class="flex flex-col mt-4">
        <!-- Affichage de l'occupant si la chambre est occupée -->
        <span class="capitalize" v-if="chambre.status === 'occupée'">
          {{ t('components.chambre.occupant') }}
          {{
            chambre.reservations && chambre.reservations.length > 0
              ? chambre.reservations[0].patient.full_name
              : ''
          }}</span
        >
        <!-- Affichage de la date de sortie prévue (sauf pour les nettoyeurs) -->
        <span
          v-if="
            role && role !== 'cleaner' && chambre.reservations && chambre.reservations.length > 0
          "
        >
          {{ t('components.chambre.sortie_prevue') }}
          {{ d(new Date(chambre.reservations[0].sortie_prevue), 'short') }}
        </span>
        <!-- Affichage de la date du dernier nettoyage -->
        <span>
          {{ t('components.chambre.dernier_nettoyage') }}
          {{ d(new Date(chambre.dernier_nettoyage), 'short') }}
        </span>
      </div>
    </template>
    <!-- Pied de la carte avec le bouton de détails du patient -->
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
