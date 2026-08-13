/** Основные разделы CRM.
 *
 * Все разделы кроме справочников — заглушки: соответствующие эндпоинты
 * на backend ещё не реализованы, и рисовать данные, которых нет, нельзя.
 */

import type { RouteRecordRaw } from 'vue-router'

export const mainRoutes: RouteRecordRaw[] = [
  {
    path: 'dashboard',
    name: 'dashboard',
    component: () => import('@/pages/dashboard/DashboardPage.vue'),
    meta: { title: 'Дашборд' },
  },
  {
    path: 'leads',
    name: 'leads',
    component: () => import('@/pages/stubs/LeadsPage.vue'),
    meta: { title: 'Лиды' },
  },
  {
    path: 'deals',
    name: 'deals',
    component: () => import('@/pages/stubs/DealsPage.vue'),
    meta: { title: 'Сделки' },
  },
  {
    path: 'clients',
    name: 'clients',
    component: () => import('@/pages/stubs/ClientsPage.vue'),
    meta: { title: 'Клиенты' },
  },
  {
    path: 'tasks',
    name: 'tasks',
    component: () => import('@/pages/stubs/TasksPage.vue'),
    meta: { title: 'Задачи' },
  },
  {
    path: 'communications',
    name: 'communications',
    component: () => import('@/pages/stubs/CommunicationsPage.vue'),
    meta: { title: 'Коммуникации' },
  },
  {
    path: 'documents',
    name: 'documents',
    component: () => import('@/pages/stubs/DocumentsPage.vue'),
    meta: { title: 'Документы' },
  },
  {
    path: 'payments',
    name: 'payments',
    component: () => import('@/pages/stubs/PaymentsPage.vue'),
    meta: { title: 'Платежи' },
  },
  {
    path: 'partners',
    name: 'partners',
    component: () => import('@/pages/stubs/PartnersPage.vue'),
    meta: { title: 'Партнёры' },
  },
  {
    path: 'analytics',
    name: 'analytics',
    component: () => import('@/pages/stubs/AnalyticsPage.vue'),
    meta: { title: 'Аналитика' },
  },
  {
    path: 'settings',
    name: 'settings',
    component: () => import('@/pages/stubs/SettingsPage.vue'),
    meta: { title: 'Настройки' },
  },
]
