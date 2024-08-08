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
      path: '/home',
      name: 'home',
      component: () => import('../views/HomeServiceLayout.vue'),
      beforeEnter: async (to, from, next) => {
        const { userStore } = await setup()
        if (userStore.role === 'nurses') {
          next()
        } else {
          next('/')
        }
      },
      children: [
        { path: '', name: 'chambres', component: () => import('../views/ChambresView.vue') },
        {
          path: ':chambreId',
          name: 'chambre',
          component: () => import('../views/ChambreDetailView.vue')
        }
      ]
    }
  ]
})

export default router
