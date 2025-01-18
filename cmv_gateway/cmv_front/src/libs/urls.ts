/**
 * @file urls.ts
 * @description URLs for the application
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const VITE_BACKEND =
  import.meta.env.VITE_ENVIRONMENT === 'dev' ? 'http://localhost:8001/api' : '/api'
console.log(VITE_BACKEND)

// L'URL de l'API d'authentification dépend de l'environnement
export const AUTH = VITE_BACKEND
