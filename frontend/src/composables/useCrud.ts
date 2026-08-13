/**
 * Состояние экрана справочника: загрузка списка, пагинация, поиск, диалоги.
 *
 * Все справочники устроены одинаково, поэтому логика живёт здесь, а экраны
 * описывают только колонки таблицы и поля формы.
 */

import { ref, shallowRef } from 'vue'

import type { CrudApi } from '@/api/reference'
import { useNotify } from '@/composables/useNotify'
import type { ListParams } from '@/types/api'

interface UseCrudOptions {
  /** Название сущности в винительном падеже для сообщений: «страну», «город». */
  entityAccusative: string
  /** Дополнительные параметры запроса списка (фильтры экрана). */
  extraParams?: () => Record<string, unknown>
}

export function useCrud<TRead extends { id: string }, TCreate, TUpdate = Partial<TCreate>>(
  api: CrudApi<TRead, TCreate, TUpdate>,
  options: UseCrudOptions,
) {
  const notify = useNotify()

  const items = shallowRef<TRead[]>([])
  const total = ref(0)
  const loading = ref(false)
  const saving = ref(false)

  const page = ref(0)
  const rows = ref(20)
  const search = ref('')

  const dialogVisible = ref(false)
  const deleteVisible = ref(false)
  const current = ref<TRead | null>(null)

  let searchTimer: ReturnType<typeof setTimeout> | undefined

  async function load(): Promise<void> {
    loading.value = true
    try {
      const params: ListParams = {
        limit: rows.value,
        offset: page.value * rows.value,
        ...(search.value ? { search: search.value } : {}),
        ...(options.extraParams?.() ?? {}),
      }
      const data = await api.list(params)
      items.value = data.items
      total.value = data.total
    } catch (error) {
      items.value = []
      total.value = 0
      notify.apiError(error, 'Не удалось загрузить список')
    } finally {
      loading.value = false
    }
  }

  function onPage(event: { page: number; rows: number }): void {
    page.value = event.page
    rows.value = event.rows
    void load()
  }

  /** Поиск с задержкой: запрос уходит после паузы в наборе, а не на каждый символ. */
  function onSearchInput(): void {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      page.value = 0
      void load()
    }, 400)
  }

  function openCreate(): void {
    current.value = null
    dialogVisible.value = true
  }

  function openEdit(item: TRead): void {
    current.value = item
    dialogVisible.value = true
  }

  function confirmDelete(item: TRead): void {
    current.value = item
    deleteVisible.value = true
  }

  async function save(payload: TCreate | TUpdate): Promise<boolean> {
    saving.value = true
    try {
      if (current.value) {
        await api.update(current.value.id, payload as TUpdate)
        notify.success(`Изменения сохранены`)
      } else {
        await api.create(payload as TCreate)
        notify.success(`Добавили ${options.entityAccusative}`)
      }
      dialogVisible.value = false
      await load()
      return true
    } catch (error) {
      notify.apiError(error, 'Не удалось сохранить изменения')
      return false
    } finally {
      saving.value = false
    }
  }

  async function remove(): Promise<void> {
    if (!current.value) return
    saving.value = true
    try {
      await api.remove(current.value.id)
      notify.success(`Удалили ${options.entityAccusative}`)
      deleteVisible.value = false
      await load()
    } catch (error) {
      notify.apiError(error, 'Не удалось удалить запись')
    } finally {
      saving.value = false
    }
  }

  return {
    items,
    total,
    loading,
    saving,
    page,
    rows,
    search,
    dialogVisible,
    deleteVisible,
    current,
    load,
    onPage,
    onSearchInput,
    openCreate,
    openEdit,
    confirmDelete,
    save,
    remove,
  }
}
