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
import Aura from '@primevue/themes/aura'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import Divider from 'primevue/divider'

progressBar(router)

const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: 'light',
      cssLayer: false
    }
  }
})
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Password', Password)
app.component('Card', Card)
app.component('Divider', Divider)

app.use(createPinia())

app.use(router)

app.mount('#app')
