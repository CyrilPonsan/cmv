/**
 * @file create-i18n-instance.ts
 * @description Helper function to create an i18n instance
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { createI18n, type LocaleMessages } from 'vue-i18n'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

// Fonction helper pour créer une nouvelle instance i18n
interface Messages {
  [key: string]: string | Messages // Permet la nested structure
}

export const createI18nInstance = (locale = 'fr') => {
  return createI18n({
    legacy: false,
    locale: locale,
    fallbackLocale: 'fr',
    messages: {
      fr: fr as unknown as LocaleMessages<Messages>,
      en: en as unknown as LocaleMessages<Messages>
    }
  })
}
