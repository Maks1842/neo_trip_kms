/** Общие типы обмена с backend. */

/** Страница списка — единый формат ответа всех коллекций API. */
export interface Page<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

/** Параметры запроса списка. */
export interface ListParams {
  limit?: number
  offset?: number
  order_by?: string
  desc?: boolean
  search?: string
  [key: string]: unknown
}

/** Единый формат тела ошибки API. */
export interface ApiErrorPayload {
  code: string
  message: string
  details: Array<{ field?: string | null; message: string; type?: string }>
  request_id: string | null
}

export interface ApiErrorResponse {
  error: ApiErrorPayload
}

/** Поля, которые есть у любой записи справочника. */
export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}
