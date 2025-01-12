<script setup lang="ts">
// Import des composants nécessaires
import { Button } from 'primevue'
import { useI18n } from 'vue-i18n'

// Initialisation du composant i18n pour les traductions
const { t } = useI18n()
</script>

<template>
  <!-- Conteneur principal avec flex layout -->
  <article class="flex-1 flex flex-col justify-evenly items-center">
    <!-- Liste des boutons de navigation -->
    <ul class="w-full p-2 flex flex-col gap-y-4">
      <!-- Bouton vers la page d'accueil -->
      <li>
        <Button
          class="w-full"
          as="router-link"
          severity="secondary"
          :label="t('app.sidebar.home')"
          to="/"
        />
      </li>
      <!-- Bouton vers la page des chambres -->
      <li>
        <Button
          class="w-full"
          as="router-link"
          severity="secondary"
          :label="t('app.sidebar.rooms')"
          to="/chambres"
        />
      </li>
      <!-- Bouton externe vers la page des rendez-vous -->
      <li>
        <Button
          class="w-full"
          as="a"
          severity="secondary"
          label="Rendez-vous"
          href="https://www.doctissimo.fr/"
          target="_blank"
        />
      </li>
    </ul>
  </article>
</template>
