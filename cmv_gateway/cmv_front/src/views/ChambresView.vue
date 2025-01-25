<script setup lang="ts">
/**
 * @file ChambresView.vue
 * @description Vue principale pour l'affichage et la gestion des chambres et services
 */

// Imports des composants
import PageHeader from '@/components/PageHeader.vue'
import ServiceItem from '@/components/ServiceItem.vue'
import useChambresList from '@/composables/useChambresList'
import { AutoComplete } from 'primevue'
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

// Récupération des fonctionnalités du composable useChambresList
const {
  getChambres,
  list,
  isLoading,
  search,
  searchValue,
  searchBySelect,
  suggestions,
  resetSearchValue
} = useChambresList()

// Composable i18n pour les traductions
const { t } = useI18n()
</script>

<template>
  <div class="min-w-screen min-h-[80vh] flex flex-col gap-y-8">
    <!-- En-tête de la page -->
    <section>
      <PageHeader :title="t('rooms.home.title')" :description="t('rooms.home.description')" />
    </section>

    <!-- Barre de recherche et bouton de rafraîchissement -->
    <section class="flex justify-between items-center">
      <!-- Titre et bouton de rafraîchissement -->
      <span class="flex items-center gap-x-4">
        <h1 class="text-2xl font-bold">{{ t('rooms.home.subtitle') }}</h1>
        <Button
          icon="pi pi-refresh"
          text
          :aria-label="t('rooms.home.button.refresh-label')"
          :loading="isLoading"
          :disabled="isLoading"
          @:click="getChambres"
        />
      </span>
      <!-- Barre de recherche avec autocomplétion -->
      <span class="flex gap-x-2 items-center">
        <AutoComplete
          size="small"
          v-model="searchValue"
          dropdown
          :suggestions="suggestions"
          @complete="search"
          @option-select="searchBySelect"
        />
        <!-- Bouton de réinitialisation de la recherche -->
        <Button
          v-show="searchValue.length > 0"
          icon="pi pi-times"
          severity="secondary"
          variant="text"
          rounded
          :aria-label="t('rooms.home.button.reset-search-label')"
          @click="resetSearchValue"
        />
      </span>
    </section>

    <!-- Liste des services et chambres -->
    <div class="flex flex-col">
      <ul class="flex flex-col gap-y-4" v-if="list.length > 0">
        <li v-for="service of list" :key="service.id_service">
          <ServiceItem v-bind="service" />
        </li>
      </ul>
    </div>
  </div>
</template>
