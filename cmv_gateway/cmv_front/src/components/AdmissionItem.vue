<script setup lang="ts">
/**
 * @file AdmissionItem.vue
 * @description Composant qui affiche les détails d'une admission d'un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type Admission from '@/models/admission'
import { Fieldset } from 'primevue'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

// Props du composant
const { admission } = defineProps<{ admission: Admission }>()

// Récupération des fonctions d'internationalisation
const { d } = useI18n()

/**
 * Calcule la légende à afficher en fonction du statut de l'admission
 * Affiche soit la date de sortie si terminée, soit la date d'entrée si en cours
 */
const legend = computed(() => {
  if (admission.sorti_le) {
    return `Terminée le ${d(admission.sorti_le, 'short')}`
  }
  return `En cours depuis le ${d(admission.entree_le, 'short')}`
})
</script>

<template>
  <!-- Conteneur principal utilisant le composant Fieldset avec la légende calculée -->
  <Fieldset :legend="legend">
    <!-- Grille pour l'affichage des informations -->
    <div class="grid grid-cols-4 gap-4 text-xs">
      <!-- Colonne des libellés -->
      <div class="flex flex-col gap-y-2 font-semibold">
        <span>Ambulatoire :</span>
        <span v-if="!admission.ambulatoire">Chambre :</span>
        <span>Entré(e) le :</span>
        <span v-if="admission.sortie_prevue_le">Sortie prévue le :</span>
        <span v-if="admission.sorti_le">Sorti(e) le :</span>
      </div>
      <!-- Colonne des valeurs -->
      <div class="flex flex-col gap-y-2">
        <span>{{ admission.ambulatoire ? 'Oui' : 'Non' }}</span>
        <span class="capitalize" v-if="!admission.ambulatoire">{{ admission.nom_chambre }}</span>
        <span>{{ d(admission.entree_le, 'short') }}</span>
        <span v-if="admission.sortie_prevue_le">{{ d(admission.sortie_prevue_le, 'short') }}</span>
        <span v-if="admission.sorti_le">{{ d(admission.sorti_le, 'short') }}</span>
      </div>
    </div>
  </Fieldset>
</template>
