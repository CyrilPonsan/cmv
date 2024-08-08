import { ref, type Ref, onUnmounted } from 'vue'
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'

import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'

interface HttpRequestOptions extends AxiosRequestConfig {
  path: string
  body?: any
  headers?: any
  method?: 'get' | 'post' | 'put' | 'delete'
}

interface UseHttp {
  isLoading: Ref<boolean>
  error: Ref<string>
  sendRequest: (req: HttpRequestOptions, applyData?: (data: any) => void) => Promise<any>
  axiosInstance: AxiosInstance
}

const useHttp = (): UseHttp => {
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')
  const userStore = useUserStore()

  // chaque requête se voit attachée le token d'authorizatopn dans ses headers
  const axiosInstance = axios.create()
  axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${userStore.access_token}`

  const sendRequest = async (
    req: HttpRequestOptions,
    applyData?: (data: any) => void
  ): Promise<any> => {
    isLoading.value = true
    error.value = ''
    let response: AxiosResponse<any>

    // TODO : ajouter les méthodes PUT et DELETE
    try {
      switch (req.method?.toLowerCase()) {
        case 'post':
          response = await axiosInstance.post(`${AUTH}${req.path}`, req.body)
          break
        default:
          response = await axiosInstance.get(`${AUTH}${req.path}`)
          break
      }

      if (applyData) {
        applyData(response.data)
      } else {
        return response.data
      }
    } catch (err: any) {
      error.value = err.response?.data.message ?? 'Erreur inconnue'

      if (err.response?.status === 403) {
        userStore.logout()
      }
    } finally {
      isLoading.value = false
    }
  }

  // gestion du rafraîchissement des tokens
  const responseInterceptor = axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      // le rafraîchissement du token a échoué
      if (error.response.status === 403 && originalRequest.url === `${AUTH}/auth/refresh`) {
        return Promise.reject(error)
      }

      // si une requête pour refresh le token n'a pas encore été effectuée on en fait une
      if (error.response.status === 403 && !originalRequest._retry) {
        // prévient qu'une nouvelle requête de refresh soit faite à nouveau si celle ci échoue
        originalRequest._retry = true

        // requête pour refresh les tokens
        const res = await axiosInstance.get(`${AUTH}/auth/refresh`, {
          headers: { Authorization: `Bearer ${userStore.refresh_token}` }
        })

        if (res.status === 200) {
          // on stock les nouveaux tokens dans le state global
          userStore.setTokens(res.data)

          // Update the axiosInstance with the new access token
          axiosInstance.defaults.headers.common['Authorization'] =
            `Bearer ${userStore.access_token}`

          // on attache le nouveau token d'accès à la requête originale
          originalRequest.headers.Authorization = `Bearer ${userStore.access_token}`

          return axiosInstance(originalRequest)
        }
      }
      return Promise.reject(error)
    }
  )

  // suppression des intercepteurs lors du démontage du composant
  onUnmounted(() => {
    axiosInstance.interceptors.response.eject(responseInterceptor)
  })

  return { isLoading, error, sendRequest, axiosInstance }
}

export default useHttp
