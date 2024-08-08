import { ref } from 'vue'
import { defineStore } from 'pinia'
import useHttp from '@/hooks/use-http'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('user', () => {
  const http = useHttp()
  const router = useRouter()

  const access_token = ref('')
  const refresh_token = ref('')
  const role = ref('')

  const handshake = () => {
    access_token.value = localStorage.getItem('access_token') ?? ''
    refresh_token.value = localStorage.getItem('refresh_token') ?? ''
    const applyData = (data: any) => {
      role.value = data.role
    }
    http.sendRequest({ path: '/users/me' }, applyData)
  }

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

  return { access_token, refresh_token, role, handshake, logout, setTokens }
})
