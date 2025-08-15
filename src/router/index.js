import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from "@/client/apiClient";

// Lazy-loaded views
const LandingView = () => import('@/views/LandingView.vue')
const LoginView   = () => import('@/views/LoginView.vue')
const SignupView  = () => import('@/views/SignupView.vue')
const AppView     = () => import('@/views/AppView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',        name: 'landing', component: LandingView },
    { path: '/login',   name: 'login',   component: LoginView,  meta: { guest: true } },
    { path: '/signup',  name: 'signup',  component: SignupView, meta: { guest: true } },
    { path: '/app',     name: 'app',     component: AppView, meta: { requiresAuth: true } },
    // { path: '/:pathMatch(.*)*', redirect: '/' } // simple 404 redirect
  ],
  scrollBehavior() { return { top: 0 } }
})

// Simple auth guards using a token in localStorage
router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next({ name: "landing", query: { next: to.fullPath } });
  } else next();
});

export default router
