<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import Button from 'primevue/button'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const userStore = useUserStore()
const { t } = useI18n()

const colorSchemeIcon = computed(() => `pi pi-${userStore.mode === 'dark' ? 'moon' : 'sun'}`)
</script>

<template>
  <div class="w-48 sticky top-0 left-0 h-screen bg-surface-900 flex flex-col justify-between">
    <h1>Sidebar</h1>
    <span>
      <Button
        :icon="colorSchemeIcon"
        aria-label="theme"
        text
        rounded
        v-tooltip.bottom="t('app.tooltip.change_mode')"
        @click="userStore.toggleColorScheme()"
      />
    </span>
  </div>
</template>
