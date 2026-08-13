/** Маршрутизация приложения. */

import { createRouter, createWebHistory } from 'vue-router'

import { mainRoutes } from '@/router/routes/main'
import { referenceRoutes } from '@/router/routes/reference'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/auth/LoginPage.vue'),
      meta: { title: 'Вход' },
    },
    {
      path: '/app',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'dashboard' } },
        ...mainRoutes,
        ...referenceRoutes,
      ],
    },
    { path: '/', redirect: { name: 'dashboard' } },
    { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  // После перезагрузки страницы токен есть, а профиля нет — восстанавливаем его
  // до проверки прав, иначе гвард отклонил бы доступ по пустому списку.
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      await auth.forceLogout()
      return { name: 'login' }
    }
  }

  if (auth.isAuthenticated && to.name === 'login') {
    return { name: 'dashboard' }
  }

  const permission = to.meta.permission as string | undefined
  if (permission && !auth.can(permission)) {
    return { name: 'dashboard' }
  }

  return true
})

router.afterEach((to) => {
  const title = to.meta.title as string | undefined
  document.title = title ? `${title} — Neo Trip CRM` : 'Neo Trip CRM'
})

export default router
