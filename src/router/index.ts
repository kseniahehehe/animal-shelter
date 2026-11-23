import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AuthView from '../components/AuthView.vue'
import QuizView from '../components/QuizView.vue'
import PetsView from '../components/PetsView.vue'
import FavoritesView from '../components/FavoritesView.vue'
import ProfileView from '../components/ProfileView.vue'
import AdminView from '../components/AdminView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/auth' },
  { path: '/auth', name: 'Auth', component: AuthView },
  { path: '/quiz', name: 'Quiz', component: QuizView, meta: { requiresAuth: true } },
  { path: '/pets', name: 'Pets', component: PetsView, meta: { requiresAuth: true } },
  { path: '/favorites', name: 'Favorites', component: FavoritesView, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const isAuthenticated = Boolean(localStorage.getItem('user_token'))
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/auth')
  } else {
    next()
  }
})

export default router