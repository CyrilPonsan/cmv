/**
 * @file router.ts
 * @description Router setup
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import LoginView from '@/views/LoginView.vue'

//  cette fonction retourne les valeurs du store nécessaires pour protéger les routes
async function setup() {
  const userStore = useUserStore()
  return { userStore }
}

export const getRoute = (role: string) => {
  switch (role) {
    case 'home':
      return 'accueil'
  }
}

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      name: 'root',
      component: LoginView,
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        if (userStore.role.length > 0) next(`/${getRoute(userStore.role)}`)
        else next()
      }
    },
    //  formulaire de connexion
    {
      path: '/accueil',
      name: 'accueil',
      component: () => import('../views/AccueilLayout.vue'),
      //  protection de la route par le rôle de l'utilisateur
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        if (userStore.role === 'home') next()
        //  si le rôle n'est pas adéquat, l'utilisateur est redirigé vers la page d'accueil
        else next('/')
      },
      children: [
        //  liste des dossiers administratifs
        {
          path: '',
          name: 'patients',
          component: () => import('../views/AccueilView.vue')
        },
        // Mise à jour d'un dossier administratif
        {
          path: '/patient/:id',
          name: 'patient',
          component: () => import('../views/PatientView.vue')
        },
        //  formulaire d'ajout d'un patient
        {
          path: '/add-patient',
          name: 'add-patient',
          component: () => import('../views/AddPatientView.vue')
        }
      ]
    }
  ]
})

export default router
