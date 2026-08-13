/**
 * HTTP-клиент приложения.
 *
 * Ключевая часть — обработка истёкшего токена. Обновление запускается один раз:
 * параллельные запросы, получившие 401, встают в очередь и повторяются с новым
 * токеном. Без этого страница с несколькими одновременными запросами выполнила бы
 * несколько обновлений подряд, а поскольку сервер применяет ротацию, все кроме
 * первого получили бы уже отозванный токен и разлогинили пользователя.
 */

import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'

import type { ApiErrorResponse } from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

/** Пути, к которым не нужно подставлять токен и на которых не нужен refresh. */
const PUBLIC_PATHS = ['/auth/login', '/auth/refresh']

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

function isPublicPath(url?: string): boolean {
  if (!url) return false
  return PUBLIC_PATHS.some((path) => url.includes(path))
}

/** Читаемое сообщение из единого формата ошибки backend. */
export function extractApiError(error: unknown, fallback = 'Не удалось выполнить операцию'): string {
  if (axios.isAxiosError(error)) {
    const payload = error.response?.data as ApiErrorResponse | undefined
    if (payload?.error) {
      const details = payload.error.details
      if (details?.length) {
        return details
          .map((item) => (item.field ? `${item.field}: ${item.message}` : item.message))
          .join('; ')
      }
      return payload.error.message
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Сервер недоступен. Проверьте, запущен ли backend'
    }
  }
  return fallback
}

// Установка обработчиков вынесена в функцию: стор и роутер импортируются
// внутри, иначе получился бы цикл модулей (стор сам использует этот клиент).
type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

let isRefreshing = false
let queue: Array<{ resolve: (token: string) => void; reject: (error: unknown) => void }> = []

function flushQueue(error: unknown, token: string | null): void {
  queue.forEach(({ resolve, reject }) => {
    if (token) resolve(token)
    else reject(error)
  })
  queue = []
}

export function setupInterceptors(): void {
  api.interceptors.request.use(async (config) => {
    const { useAuthStore } = await import('@/stores/auth')
    const auth = useAuthStore()
    if (auth.accessToken && !isPublicPath(config.url)) {
      config.headers.Authorization = `Bearer ${auth.accessToken}`
    }
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const original = error.config as RetriableConfig | undefined

      if (!original || error.response?.status !== 401 || isPublicPath(original.url)) {
        return Promise.reject(error)
      }
      if (original._retry) {
        return Promise.reject(error)
      }

      const { useAuthStore } = await import('@/stores/auth')
      const auth = useAuthStore()

      if (!auth.refreshToken) {
        await auth.forceLogout()
        return Promise.reject(error)
      }

      // Обновление уже идёт — ждём его результата, а не запускаем своё.
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          queue.push({ resolve, reject })
        }).then((token) => {
          original._retry = true
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
      }

      original._retry = true
      isRefreshing = true

      try {
        const token = await auth.refresh()
        flushQueue(null, token)
        original.headers.Authorization = `Bearer ${token}`
        return await api(original)
      } catch (refreshError) {
        flushQueue(refreshError, null)
        await auth.forceLogout()
        return await Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    },
  )
}

export default api
