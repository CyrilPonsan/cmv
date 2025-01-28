/**
 * @file main.ts
 * @description Point d'entrée principal de l'application Vue.js
 */

/* eslint-disable vue/no-reserved-component-names */
/* eslint-disable vue/multi-word-component-names */

// Import des styles
import './assets/main.css'
import 'nprogress/nprogress.css'
import 'primeicons/primeicons.css'

// Import des dépendances Vue
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import des plugins et composants
import progressBar from './includes/progress-bar'
import PrimeVue from 'primevue/config'
import Lara from '@primevue/themes/lara'
import ToastService from 'primevue/toastservice'
import i18n from './includes/i18n'
import Tooltip from 'primevue/tooltip'

// Initialisation de la barre de progression
progressBar(router)

// Création de l'application Vue
const app = createApp(App)

// Configuration des plugins
app.use(i18n)
app.use(PrimeVue, {
  theme: {
    preset: Lara,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark',
      cssLayer: false
    }
  }
})

// Ajout des directives et services
app.directive('tooltip', Tooltip)
app.use(ToastService)
app.use(createPinia())
app.use(router)

// Montage de l'application sur l'élément #app
app.mount('#app')
