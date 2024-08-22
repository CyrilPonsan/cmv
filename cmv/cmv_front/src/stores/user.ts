import { ref } from 'vue'
import { defineStore } from 'pinia'
import useHttp from '@/composables/use-http2'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('user', () => {
  const http = useHttp()
  const router = useRouter()

  const access_token = ref('')
  const refresh_token = ref('')
  const role = ref('')
  const mode = ref('light')

  /**
   * alterne ente le mode clair et le mode sombre
   */
  const toggleColorScheme = () => {
    const element = document.querySelector('html')

    if (element) {
      element.classList.toggle('my-app-dark')
      if (element.classList.value === 'my-app-dark') {
        //  si on passe au mode sombrer on enregistre le changement dans le session storage
        localStorage.setItem('color-scheme', 'my-app-dark')
        mode.value = 'dark'
      }
      //  si on revient au mode lumineux on retire l'entrée du storage
      else {
        localStorage.removeItem('color-scheme')
        mode.value = 'light'
      }
    }
  }

  //  au démarrage de l'application on vérifie le mode d'affichage à utiliser
  const updateColorScheme = () => {
    //  récupération de la valeur du mode d'affichage stocké dans le storage
    const colorScheme = localStorage.getItem('color-scheme')
    //  si une valeur est trouvée on switch sur le mode sombre
    if (colorScheme && colorScheme === 'my-app-dark') {
      mode.value = 'dark'
      const element = document.querySelector('html')
      if (element) element.classList.toggle('my-app-dark')
    } else {
      mode.value = 'light'
    }
  }

  /**
   * met à jour le mode d'affichage en fonction des préférences de l'utilisateur qui sont sotckées dans le storage
   * vérification de la validité des jetons de session stockés dans le storage en effectuant une requête auprès de l'api
   */
  const handshake = () => {
    updateColorScheme()
    access_token.value = localStorage.getItem('access_token') ?? ''
    refresh_token.value = localStorage.getItem('refresh_token') ?? ''
    getUserInfos()
  }

  /**
   * envoie une requête à l'api pour récupérer le role de l'utilisateur
   */
  const getUserInfos = () => {
    const applyData = (data: any) => {
      role.value = data.role
    }
    http.sendRequest({ path: '/users/me' }, applyData)
  }

  /**
   * met à jour les valeurs des jetons de sessions en mémoire et dans le storage
   * @param value { access_token: string; refresh_token: string }
   */
  const setTokens = (value: { access_token: string; refresh_token: string }) => {
    access_token.value = value.access_token
    refresh_token.value = value.refresh_token
    localStorage.setItem('access_token', value.access_token)
    localStorage.setItem('refresh_token', value.refresh_token)
  }

  const logout = () => {
    localStorage.setItem('access_token', '')
    localStorage.setItem('refresh_token', '')
    role.value = ''
    console.log('disconnected!')
    router.push('/')
  }

  return {
    access_token,
    mode,
    refresh_token,
    role,
    getUserInfos,
    handshake,
    logout,
    setTokens,
    toggleColorScheme
  }
})
