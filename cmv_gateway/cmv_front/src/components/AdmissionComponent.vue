<script setup lang="ts">
import type Admission from '@/models/admission'
import { Fieldset } from 'primevue'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const { admission } = defineProps<{ admission: Admission }>()

const { d } = useI18n()

const legend = computed(() => {
  if (admission.sorti_le) {
    return `Terminée le ${d(admission.sorti_le, 'short')}`
  }
  return `En cours depuis le ${d(admission.entree_le, 'short')}`
})
</script>

<template>
  <Fieldset :legend="legend">
    <div class="grid grid-cols-4 gap-4 text-xs">
      <div class="flex flex-col gap-y-2 font-semibold">
        <span>Ambulatoire :</span>
        <span v-if="!admission.ambulatoire">Chambre :</span>
        <span>Entré(e) le :</span>
        <span v-if="admission.sortie_prevue_le">Sortie prévue le :</span>
        <span v-if="admission.sorti_le">Sorti(e) le :</span>
      </div>
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
