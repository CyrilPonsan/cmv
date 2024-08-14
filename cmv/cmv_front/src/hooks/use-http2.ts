import { useUserStore } from '@/stores/user'
import { ref } from 'vue'

type HttpRequestOptions = {
  path: string
  body?: any
  headers?: any
  method?: 'get' | 'post' | 'put' | 'delete'
}

const useHttp = () => {
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')
  const userStore = useUserStore()

  const sendRequest = async <T>(
    req: HttpRequestOptions,
    applyData?: (data: T) => void
  ): Promise<any> => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await getData(req)
        const responseJson = await response.json()
        console.log({responseJson});
        
      if (!response.ok) {
        if (response.status === 403) {
          const result = await refreshToken()
          const resultJson = await result.json()
          if (result.ok) {
            userStore.setTokens(resultJson)
            const data = await cloneRequest(req)
            const dataJson = await data.json()
            if (!data.ok) {
              throw { statusCode: data.status, message: "pwet" }
            }
          }
        }
      }
      if (applyData) {
        console.log({ responseJson })

        applyData(responseJson)
      }
    } catch (error: any) {
      console.log("toto", error)
    } finally {
      isLoading.value = false
    }
  }

  const getData = async (req: HttpRequestOptions): Promise<Response> => {
    let response: Response
    switch (req.method?.toLocaleLowerCase()) {
        case 'post':
            console.log("hi");
            
        response = await fetch(`/api/${req.path}`, {
          method: 'post',
          body: JSON.stringify(req.body!),
          headers: {
            Authorization: `Bearer ${userStore.access_token}`,
            'Content-Type': 'application/json'
          }
        })
        default:
            console.log("hello");
      
        response = await fetch(`/api/${req.path}`, {
          headers: {
            Authorization: `Bearer ${userStore.access_token}`
          }
        })
            
    }
    return response
  }

  const refreshToken = async (): Promise<Response> => {
    const response = await fetch('/api/auth/refresh', {
      headers: {
        Authorization: `Bearer ${userStore.refresh_token}`
      }
    })
    return response
  }

  const cloneRequest = async (req: HttpRequestOptions): Promise<Response> => {
    const response = await fetch(`/api/${req.path}`, {
      method: req.method ?? 'get',
      body: req.body,
      headers: {
        Authorization: `Bearer ${userStore.access_token}`
      }
    })
    return response
  }
  return { sendRequest, isLoading }
}

export default useHttp
