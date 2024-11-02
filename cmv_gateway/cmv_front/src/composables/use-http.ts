import { ref, type Ref } from 'vue'
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
    withCredentials: true, // This ensures cookies are sent with every request
    baseURL: AUTH
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

      if (err.response?.status === 403) {
        userStore.logout()
      }
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, error, sendRequest, axiosInstance }
}

export default useHttp
