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
    const response = await getData(req);
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      const responseJson = await response.json();

      if (response.ok) {
        if (applyData) {
          applyData(responseJson);
        }
      } else {
        // Gérer les erreurs de réponse non-ok ici
        throw new Error(`Request failed with status ${response.status}`);
      }
    } else {
      // Gérer le cas où la réponse n'est pas du JSON
      throw new Error('Le serveur a renvoyé un type de contenu inattendu.');
    }
  } catch (error: any) {
    console.error("An error occurred:", error.message || error);
    error.value = error.message || 'An unknown error occurred';
  } finally {
    isLoading.value = false;
  }
}


const getData = async (req: HttpRequestOptions): Promise<Response> => {
  const headers: any = {
    Authorization: `Bearer ${userStore.access_token}`,
    'Content-Type': 'application/json',  // Assurez-vous que c'est correct pour votre API
    'Accept': 'application/json',
    ...req.headers // Ajouter d'autres en-têtes si nécessaires
  };

  return await fetch(`/api/${req.path}`, {
    method: req.method || 'get',
    body: req.body ? JSON.stringify(req.body) : undefined,
    headers: {
      Authorization: `Bearer ${userStore.access_token}`,
      'Content-Type': 'application/json',  // Assurez-vous que c'est correct pour votre API}
      'Accept': 'application/json'
    }
  })
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
  const clonedHeaders = {
    ...req.headers,
    Authorization: `Bearer ${userStore.access_token}`
  };
  return fetch(`/api/${req.path}`, {
    method: req.method ?? 'get',
    body: req.body ? JSON.stringify(req.body) : undefined,
    headers: clonedHeaders
  });
}

  return { sendRequest, isLoading }
}

export default useHttp
