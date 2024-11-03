import { ref, type Ref, onUnmounted } from 'vue'
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'

import { AUTH } from '@/libs/urls'
import { useUserStore } from '@/stores/user'

type HttpMethod = 'get' | 'post' | 'put' | 'delete'

interface HttpRequestOptions extends AxiosRequestConfig {
  path: string
  body?: any
  headers?: Record<string, string>
  method?: HttpMethod
}

export interface UseHttp {
  isLoading: Ref<boolean>
  error: Ref<string | null>
  sendRequest: <T>(req: HttpRequestOptions, applyData?: (data: T) => void) => Promise<T | undefined>
  axiosInstance: AxiosInstance
}

const useHttp = (): UseHttp => {
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const userStore = useUserStore()
  const axiosInstance = axios.create({
    withCredentials: true,
    baseURL: AUTH
  })

  const responseInterceptor = axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (!error.response) {
        return Promise.reject(error)
      }

      const originalRequest = error.config
      console.log('Response interceptor - Error status:', error.response.status)
      console.log('Original request URL:', originalRequest.url)

      // Si c'est une erreur sur le refresh token lui-même, on rejette directement
      if (
        (error.response.status === 403 || error.response.status === 401) &&
        originalRequest.url === '/auth/refresh'
      ) {
        console.log('Error on refresh token request - logging out')
        userStore.logout()
        return Promise.reject(error)
      }

      // Pour les autres erreurs 401/403, on tente de rafraîchir le token
      if (
        (error.response.status === 403 || error.response.status === 401) &&
        !originalRequest._retry
      ) {
        console.log('Attempting to refresh token')
        originalRequest._retry = true

        try {
          const res = await axiosInstance.get('/auth/refresh')
          if (res.status === 200) {
            console.log('Token refreshed successfully - retrying original request')
            return axiosInstance(originalRequest)
          }
        } catch (refreshError) {
          console.log('Token refresh failed - logging out')
          userStore.logout()
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )

  onUnmounted(() => {
    axiosInstance.interceptors.response.eject(responseInterceptor)
  })

  const sendRequest = async <T>(
    req: HttpRequestOptions,
    applyData?: (data: T) => void
  ): Promise<T | undefined> => {
    isLoading.value = true
    error.value = null

    try {
      const { method = 'get', path, body, ...config } = req
      const response: AxiosResponse<T> = await axiosInstance.request({
        method,
        url: path,
        data: body,
        ...config
      })

      if (applyData) {
        applyData(response.data)
      } else {
        return response.data
      }
    } catch (err: any) {
      error.value = err.response?.data.message ?? 'Erreur inconnue'
      throw err // On propage l'erreur pour que l'intercepteur puisse la gérer
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, error, sendRequest, axiosInstance }
}

export default useHttp
