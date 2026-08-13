/** Стор авторизации. */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import type { CurrentUser } from '@/types/auth'

const ACCESS_KEY = 'neo_trip_access_token'
const REFRESH_KEY = 'neo_trip_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string>(localStorage.getItem(ACCESS_KEY) ?? '')
  const refreshToken = ref<string>(localStorage.getItem(REFRESH_KEY) ?? '')
  const user = ref<CurrentUser | null>(null)

  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const permissions = computed(() => user.value?.role.permissions ?? [])

  /**
   * Проверка права. Профиль и права запрашиваются у сервера, а не извлекаются
   * из JWT на клиенте: содержимое токена не должно быть источником решений
   * о доступе, иначе изменение прав не применится до перевыпуска токена.
   */
  function can(code: string): boolean {
    return permissions.value.includes('*') || permissions.value.includes(code)
  }

  function setTokens(access: string, refresh: string): void {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  }

  function clearTokens(): void {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(email: string, password: string): Promise<void> {
    const { data } = await authApi.login(email, password)
    setTokens(data.access_token, data.refresh_token)
    await fetchMe()
  }

  async function fetchMe(): Promise<void> {
    const { data } = await authApi.me()
    user.value = data
  }

  /** Обновление пары токенов. Возвращает новый токен доступа. */
  async function refresh(): Promise<string> {
    const { data } = await authApi.refresh(refreshToken.value)
    setTokens(data.access_token, data.refresh_token)
    return data.access_token
  }

  async function logout(): Promise<void> {
    if (refreshToken.value) {
      // Ошибку выхода игнорируем: токен мог протухнуть, но локальную сессию
      // всё равно нужно завершить.
      await authApi.logout(refreshToken.value).catch(() => undefined)
    }
    clearTokens()
  }

  /** Принудительное завершение сессии — вызывается из перехватчика 401. */
  async function forceLogout(): Promise<void> {
    clearTokens()
    const { default: router } = await import('@/router')
    if (router.currentRoute.value.name !== 'login') {
      await router.push({ name: 'login' })
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    permissions,
    can,
    login,
    fetchMe,
    refresh,
    logout,
    forceLogout,
    setTokens,
    clearTokens,
  }
})
