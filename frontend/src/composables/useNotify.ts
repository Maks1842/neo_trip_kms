/**
 * Единая точка показа уведомлений.
 *
 * Компоненты никогда не вызывают toast.add напрямую: формат, длительность и
 * разбор ошибок API описаны здесь один раз, а не копируются по экранам.
 */

import { useToast } from 'primevue/usetoast'

import { extractApiError } from '@/api/client'

const LIFE = 3500

export function useNotify() {
  const toast = useToast()

  return {
    success(detail: string, summary = 'Готово'): void {
      toast.add({ severity: 'success', summary, detail, life: LIFE })
    },
    info(detail: string, summary = 'Информация'): void {
      toast.add({ severity: 'info', summary, detail, life: LIFE })
    },
    warn(detail: string, summary = 'Внимание'): void {
      toast.add({ severity: 'warn', summary, detail, life: LIFE })
    },
    error(detail: string, summary = 'Ошибка'): void {
      toast.add({ severity: 'error', summary, detail, life: LIFE + 2000 })
    },
    /** Показывает ошибку API в человекочитаемом виде. */
    apiError(error: unknown, fallback?: string): void {
      toast.add({
        severity: 'error',
        summary: 'Ошибка',
        detail: extractApiError(error, fallback),
        life: LIFE + 2000,
      })
    },
  }
}
