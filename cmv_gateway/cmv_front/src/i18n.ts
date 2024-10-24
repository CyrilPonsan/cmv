import { createI18n, type LocaleMessages } from 'vue-i18n'
import fr from './locales/fr.json'

// Définir l'interface pour vos messages
interface Messages {
  [key: string]: string | Messages // Permet la nested structure
}

const i18n = createI18n<[Messages], 'fr'>({
  locale: 'fr',
  fallbackLocale: 'fr',
  messages: {
    fr: fr as unknown as LocaleMessages<Messages>
  },
  legacy: false
})

export default i18n
