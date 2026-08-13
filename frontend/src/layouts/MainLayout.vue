<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import type { MenuItem } from 'primevue/menuitem'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

interface NavItem {
  label: string
  icon: string
  to?: string
  permission?: string
  children?: NavItem[]
  section?: string
}

const MOBILE_BREAKPOINT = 768
const COLLAPSE_KEY = 'neo_trip_sidebar_collapsed'

const auth = useAuthStore()
const theme = useThemeStore()
const route = useRoute()
const router = useRouter()

const collapsed = ref(localStorage.getItem(COLLAPSE_KEY) === '1')
const mobileOpen = ref(false)
const referenceOpen = ref(route.path.includes('/reference/'))
const profileMenu = ref<InstanceType<typeof Menu> | null>(null)

// Полный состав разделов. Реальный функционал пока только у справочников,
// остальные пункты ведут на заглушки — так проверяется каркас навигации.
const allItems: NavItem[] = [
  { label: 'Дашборд', icon: 'pi pi-home', to: '/app/dashboard' },
  { section: 'Работа с клиентами', label: '', icon: '' },
  { label: 'Лиды', icon: 'pi pi-inbox', to: '/app/leads' },
  { label: 'Сделки', icon: 'pi pi-briefcase', to: '/app/deals' },
  { label: 'Клиенты', icon: 'pi pi-users', to: '/app/clients' },
  { label: 'Задачи', icon: 'pi pi-check-square', to: '/app/tasks' },
  { label: 'Коммуникации', icon: 'pi pi-comments', to: '/app/communications' },
  { section: 'Финансы и документы', label: '', icon: '' },
  { label: 'Документы', icon: 'pi pi-file', to: '/app/documents' },
  { label: 'Платежи', icon: 'pi pi-wallet', to: '/app/payments' },
  { label: 'Партнёры', icon: 'pi pi-share-alt', to: '/app/partners' },
  { label: 'Аналитика', icon: 'pi pi-chart-bar', to: '/app/analytics' },
  { section: 'Администрирование', label: '', icon: '' },
  {
    label: 'Справочники',
    icon: 'pi pi-book',
    permission: 'reference.read',
    children: [
      { label: 'Страны', icon: 'pi pi-globe', to: '/app/reference/countries' },
      { label: 'Города', icon: 'pi pi-map-marker', to: '/app/reference/cities' },
      { label: 'Валюты', icon: 'pi pi-dollar', to: '/app/reference/currencies' },
      { label: 'Объекты размещения', icon: 'pi pi-building', to: '/app/reference/accommodations' },
      { label: 'Программы', icon: 'pi pi-th-large', to: '/app/reference/accommodation-programs' },
      { label: 'Тарифы', icon: 'pi pi-tags', to: '/app/reference/tariff-entries' },
      { label: 'Этапы воронок', icon: 'pi pi-sitemap', to: '/app/reference/deal-stages' },
      { label: 'Партнёры', icon: 'pi pi-id-card', to: '/app/reference/partners' },
      { label: 'Шаблоны документов', icon: 'pi pi-copy', to: '/app/reference/document-templates' },
      { label: 'Роли', icon: 'pi pi-lock', to: '/app/reference/roles', permission: 'roles.read' },
    ],
  },
  { label: 'Настройки', icon: 'pi pi-cog', to: '/app/settings' },
]

function isAllowed(item: NavItem): boolean {
  return !item.permission || auth.can(item.permission)
}

const menuItems = computed<NavItem[]>(() =>
  allItems.filter(isAllowed).map((item) => ({
    ...item,
    children: item.children?.filter(isAllowed),
  })),
)

const pageTitle = computed(() => (route.meta.title as string | undefined) ?? '')
const userInitials = computed(() => {
  const name = auth.user?.full_name ?? ''
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
})

const profileItems = computed<MenuItem[]>(() => [
  { label: auth.user?.email ?? '', disabled: true },
  { separator: true },
  {
    label: 'Выйти',
    icon: 'pi pi-sign-out',
    command: async () => {
      await auth.logout()
      await router.push({ name: 'login' })
    },
  },
])

function toggleSidebar(): void {
  if (window.innerWidth <= MOBILE_BREAKPOINT) {
    mobileOpen.value = !mobileOpen.value
  } else {
    collapsed.value = !collapsed.value
    localStorage.setItem(COLLAPSE_KEY, collapsed.value ? '1' : '0')
  }
}

function closeMobile(): void {
  mobileOpen.value = false
}

function handleResize(): void {
  if (window.innerWidth > MOBILE_BREAKPOINT) mobileOpen.value = false
}

onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))

// Переход по ссылке на узком экране должен закрывать выдвинутый сайдбар.
watch(() => route.fullPath, closeMobile)
</script>

<template>
  <div
    class="app-layout"
    :class="{
      'app-layout--collapsed': collapsed,
      'app-layout--mobile-open': mobileOpen,
    }"
  >
    <div v-if="mobileOpen" class="app-layout__backdrop" @click="closeMobile" />

    <aside class="app-layout__sidebar">
      <div class="app-layout__brand">
        <i class="pi pi-compass" style="color: var(--p-primary-color)" />
        <span class="app-layout__brand-text">Neo Trip</span>
      </div>

      <nav class="app-layout__nav">
        <template v-for="(item, index) in menuItems" :key="item.section ?? item.to ?? index">
          <div v-if="item.section" class="app-layout__section">{{ item.section }}</div>

          <RouterLink v-else-if="item.to" :to="item.to" class="app-layout__item">
            <i :class="[item.icon, 'app-layout__item-icon']" />
            <span class="app-layout__item-label">{{ item.label }}</span>
          </RouterLink>

          <template v-else-if="item.children">
            <button
              type="button"
              class="app-layout__item"
              @click="referenceOpen = !referenceOpen"
            >
              <i :class="[item.icon, 'app-layout__item-icon']" />
              <span class="app-layout__item-label">{{ item.label }}</span>
              <i
                class="pi app-layout__item-toggle"
                :class="referenceOpen ? 'pi-chevron-down' : 'pi-chevron-right'"
              />
            </button>

            <div v-show="referenceOpen" class="app-layout__submenu">
              <RouterLink
                v-for="child in item.children"
                :key="child.to"
                :to="child.to!"
                class="app-layout__item"
              >
                <i :class="[child.icon, 'app-layout__item-icon']" />
                <span class="app-layout__item-label">{{ child.label }}</span>
              </RouterLink>
            </div>
          </template>
        </template>
      </nav>

      <div class="app-layout__footer">
        <div class="text-muted" style="font-size: 0.8rem">
          <span class="app-layout__item-label">{{ auth.user?.company.name }}</span>
        </div>
      </div>
    </aside>

    <div class="app-layout__main">
      <header class="app-layout__topbar">
        <Button
          icon="pi pi-bars"
          text
          rounded
          aria-label="Меню"
          @click="toggleSidebar"
        />
        <span class="app-layout__topbar-title">{{ pageTitle }}</span>

        <div class="app-layout__topbar-spacer" />

        <Button
          :icon="theme.isDark ? 'pi pi-sun' : 'pi pi-moon'"
          text
          rounded
          :aria-label="theme.isDark ? 'Светлая тема' : 'Тёмная тема'"
          @click="theme.toggle()"
        />

        <Button text rounded aria-label="Профиль" @click="profileMenu?.toggle($event)">
          <Avatar :label="userInitials" shape="circle" size="normal" />
        </Button>
        <Menu ref="profileMenu" :model="profileItems" :popup="true" />
      </header>

      <main class="app-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
