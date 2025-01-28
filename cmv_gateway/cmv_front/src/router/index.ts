/**
 * @file router.ts
 * @description Configuration du routeur Vue avec protection des routes par rôles utilisateur
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import LoginView from '@/views/LoginView.vue'

/**
 * Initialise et retourne le store utilisateur pour la protection des routes
 * @returns {Promise<{userStore: any}>} Le store utilisateur
 */
async function setup() {
  const userStore = useUserStore()
  return { userStore }
}

/**
 * Détermine la route de redirection en fonction du rôle utilisateur
 * @param {string} role - Le rôle de l'utilisateur
 * @returns {string} Le chemin de redirection
 */
export const getRoute = (role: string) => {
  switch (role) {
    case 'home':
      return 'accueil'
  }
}

// Configuration du routeur Vue
const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    // Route racine - Page de connexion
    {
      path: '/',
      name: 'root',
      component: LoginView,
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        // Redirection si l'utilisateur est déjà connecté
        if (userStore.role.length > 0) next(`/${getRoute(userStore.role)}`)
        else next()
      }
    },
    // Route pour créer une nouvelle admission
    {
      path: '/admissions/create/:patientId',
      name: 'admissions-create',
      component: () => import('../views/AdmissionView.vue')
    },
    // Route 404 - Page non trouvée
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFound.vue')
    },
    // Section Accueil - Gestion des patients
    {
      path: '/accueil',
      name: 'accueil',
      component: () => import('../views/AccueilLayout.vue'),
      // Protection de la route - Accès réservé au rôle 'home'
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        if (userStore.role === 'home') next()
        else next('/') // Redirection vers la page de connexion si non autorisé
      },
      children: [
        // Liste des dossiers patients
        {
          path: '',
          name: 'patients',
          component: () => import('../views/AccueilView.vue')
        },
        // Détails d'un dossier patient spécifique
        {
          path: '/patient/:id',
          name: 'patient',
          component: () => import('../views/PatientView.vue')
        },
        // Formulaire de création d'un nouveau patient
        {
          path: '/add-patient',
          name: 'add-patient',
          component: () => import('../views/AddPatientView.vue')
        }
      ]
    },
    // Section Chambres - Gestion des chambres
    {
      path: '/chambres',
      name: 'chambres-layout',
      component: () => import('../views/ChambresLayout.vue'),
      // Protection de la route - Accès multiple (home, nurses, cleaning)
      beforeEnter: async (_to, _from, next) => {
        const { userStore } = await setup()
        const allowedRoles = ['home', 'nurses', 'cleaning']
        if (allowedRoles.includes(userStore.role)) next()
        else next('/') // Redirection vers la page de connexion si non autorisé
      },
      children: [
        // Vue principale des chambres
        {
          path: '',
          name: 'chambres',
          component: () => import('../views/ChambresView.vue')
        }
      ]
    }
  ]
})

export default router
