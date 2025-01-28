/**
 * @file use-http.ts
 * @description Composable pour gérer les requêtes HTTP avec gestion automatique des tokens
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { ref, type Ref, onUnmounted } from 'vue'
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'

import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

/**
 * Interface étendant AxiosRequestConfig pour ajouter des options spécifiques
 * @property path - Chemin de la requête
 * @property body - Corps de la requête (optionnel)
 * @property headers - En-têtes HTTP personnalisés (optionnel)
 */
interface HttpRequestOptions extends AxiosRequestConfig {
  path: string
  body?: any | FormData
  headers?: Record<string, string>
}

/**
 * Interface exposée par le composable useHttp
 * @property isLoading - État de chargement de la requête
 * @property error - Message d'erreur éventuel
 * @property sendRequest - Fonction pour envoyer une requête HTTP
 * @property axiosInstance - Instance Axios configurée
 */
export type UseHttp = {
  isLoading: Ref<boolean>
  error: Ref<string | null>
  sendRequest: <T>(req: HttpRequestOptions, applyData?: (data: T) => void) => Promise<T | undefined>
  axiosInstance: AxiosInstance
}

/**
 * Composable pour gérer les requêtes HTTP
 * Gère automatiquement le rafraîchissement des tokens et les erreurs
 */
const useHttp = (): UseHttp => {
  const router = useRouter()
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const userStore = useUserStore()

  // Configuration de base de l'instance Axios
  const axiosInstance = axios.create({
    withCredentials: true,
    baseURL: AUTH
  })

  /**
   * Intercepteur de réponse pour gérer:
   * - Les erreurs réseau
   * - Le rafraîchissement automatique des tokens
   * - La déconnexion en cas d'échec d'AUTHentification
   */
  const responseInterceptor = axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (!error.response) {
        return Promise.reject(error)
      }

      const originalRequest = error.config
      console.log('Response interceptor - Error status:', error.response.status)
      console.log('Original request URL:', originalRequest.url)

      // Redirection en cas d'erreur serveur
      if (error.response.status >= 500) {
        router.push({ name: 'network-issue' })
      }

      // Gestion des erreurs de rafraîchissement de token
      if (error.response.status === 403 && originalRequest.url === `/auth/refresh`) {
        console.log('Error on refresh token request - logging out')
        userStore.logout()
        return Promise.reject(error)
      }

      // Tentative de rafraîchissement du token pour les autres erreurs d'AUTHentification
      if (error.response.status === 403 && !originalRequest._retry) {
        console.log('Attempting to refresh token')
        originalRequest._retry = true

        try {
          const res = await axiosInstance.get('/auth/refresh')
          if (res.status === 200) {
            console.log('Token refreshed successfully - retrying original request')
            return await axiosInstance(originalRequest)
          }
        } catch (refreshError) {
          console.log('Token refresh failed - logging out', refreshError)
          userStore.logout()
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )

  // Nettoyage des intercepteurs à la destruction du composant
  onUnmounted(() => {
    axiosInstance.interceptors.response.eject(responseInterceptor)
  })

  /**
   * Envoie une requête HTTP avec gestion des erreurs et du chargement
   * @param req - Options de la requête
   * @param applyData - Callback optionnel pour traiter les données reçues
   * @returns Les données de la réponse ou undefined si un callback est fourni
   */
  const sendRequest = async <T>(
    req: HttpRequestOptions,
    applyData?: (data: T) => void
  ): Promise<T | undefined> => {
    isLoading.value = true
    error.value = null

    try {
      const { method = 'get', path, body, headers = {}, ...config } = req

      // Gestion automatique du Content-Type pour FormData
      const requestHeaders =
        body instanceof FormData ? headers : { 'Content-Type': 'application/json', ...headers }

      const response: AxiosResponse<T> = await axiosInstance.request({
        method,
        url: path,
        data: body,
        headers: requestHeaders,
        ...config
      })

      if (applyData) {
        applyData(response.data)
      } else {
        return response.data
      }
    } catch (err: any) {
      error.value = err.response?.data.detail ?? 'unknown_error'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Interface publique du composable
  return { isLoading, error, sendRequest, axiosInstance }
}

export default useHttp
