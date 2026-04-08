import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8', // Utilise le moteur qu'on vient d'installer
      reporter: ['text', 'json', 'html'], // 'html' va te générer un beau dossier avec l'UI
      exclude: ['node_modules/', 'tests/'] // Exclure les fichiers de test eux-mêmes
      // all: true, // Décommente ça si tu veux que les fichiers non testés apparaissent aussi à 0%
    }
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@stores': path.resolve(__dirname, './src/stores')
    }
  }
})
