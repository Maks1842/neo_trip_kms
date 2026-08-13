/** Маршруты справочников. */

import type { RouteRecordRaw } from 'vue-router'

const READ = 'reference.read'

export const referenceRoutes: RouteRecordRaw[] = [
  {
    path: 'reference/countries',
    name: 'reference-countries',
    component: () => import('@/pages/reference/CountriesPage.vue'),
    meta: { title: 'Страны', permission: READ },
  },
  {
    path: 'reference/cities',
    name: 'reference-cities',
    component: () => import('@/pages/reference/CitiesPage.vue'),
    meta: { title: 'Города', permission: READ },
  },
  {
    path: 'reference/currencies',
    name: 'reference-currencies',
    component: () => import('@/pages/reference/CurrenciesPage.vue'),
    meta: { title: 'Валюты', permission: READ },
  },
  {
    path: 'reference/accommodations',
    name: 'reference-accommodations',
    component: () => import('@/pages/reference/AccommodationsPage.vue'),
    meta: { title: 'Объекты размещения', permission: READ },
  },
  {
    path: 'reference/accommodation-programs',
    name: 'reference-accommodation-programs',
    component: () => import('@/pages/reference/AccommodationProgramsPage.vue'),
    meta: { title: 'Программы размещения', permission: READ },
  },
  {
    path: 'reference/tariff-entries',
    name: 'reference-tariff-entries',
    component: () => import('@/pages/reference/TariffEntriesPage.vue'),
    meta: { title: 'Тарифы', permission: READ },
  },
  {
    path: 'reference/deal-stages',
    name: 'reference-deal-stages',
    component: () => import('@/pages/reference/DealStagesPage.vue'),
    meta: { title: 'Этапы воронок', permission: READ },
  },
  {
    path: 'reference/partners',
    name: 'reference-partners',
    component: () => import('@/pages/reference/PartnersPage.vue'),
    meta: { title: 'Партнёры', permission: READ },
  },
  {
    path: 'reference/document-templates',
    name: 'reference-document-templates',
    component: () => import('@/pages/reference/DocumentTemplatesPage.vue'),
    meta: { title: 'Шаблоны документов', permission: READ },
  },
  {
    path: 'reference/roles',
    name: 'reference-roles',
    component: () => import('@/pages/reference/RolesPage.vue'),
    meta: { title: 'Роли', permission: 'roles.read' },
  },
]
