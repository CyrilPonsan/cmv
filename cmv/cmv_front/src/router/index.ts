import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useUserStore } from '@/stores/user'

// Define the setup function
async function setup() {
  const userStore = useUserStore()
  return { userStore }
}

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      name: 'root',
      component: HomeView
    },
    {
      path: '/accueil',
      name: 'accueil',
      component: () => import('../views/AccueilLayout.vue'),
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        if (userStore.role === 'home') next()
        else next('/')
      },
      children: [
        {
          path: '',
          name: 'patients',
          component: () => import('../views/AccueilView.vue')
        }
      ]
    }
  ]
})

export default router
