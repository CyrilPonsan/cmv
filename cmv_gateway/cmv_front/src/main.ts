/* eslint-disable vue/no-reserved-component-names */
/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import progressBar from './includes/progress-bar'
import 'nprogress/nprogress.css'
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'
import Lara from '@primevue/themes/lara'
import ToastService from 'primevue/toastservice'
import i18n from './includes/i18n'
import Tooltip from 'primevue/tooltip'

progressBar(router)

const app = createApp(App)
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
app.directive('tooltip', Tooltip)
app.use(ToastService)
app.use(createPinia())
app.use(router)
app.mount('#app')
