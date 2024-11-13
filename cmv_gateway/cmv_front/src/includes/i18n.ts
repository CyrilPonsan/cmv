/**
 * @file i18n.ts
 * @description Internationalization setup
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { createI18n, type LocaleMessages } from 'vue-i18n'
import fr from '@/locales/fr.json'
import en from '@/locales/en.json'

// Définir l'interface pour vos messages
interface Messages {
  [key: string]: string | Messages // Permet la nested structure
}

const i18n = createI18n<[Messages], 'fr' | 'en'>({
  locale: 'fr',
  datetimeFormats: {
    fr: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    },
    en: {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }
    }
  },
  fallbackLocale: 'fr',
  messages: {
    fr: fr as unknown as LocaleMessages<Messages>,
    en: en as unknown as LocaleMessages<Messages>
  },
  legacy: false
})

export default i18n
