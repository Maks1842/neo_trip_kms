/** Описание экрана справочника: колонки таблицы и поля формы. */

export type FormValues = Record<string, unknown>

export interface SelectOption {
  label: string
  value: string | number
}

export interface CrudColumn {
  field: string
  header: string
  /** Способ отображения значения в таблице. */
  type?: 'text' | 'boolean' | 'options' | 'color'
  width?: string
  sortable?: boolean
  /** Для type: 'options' — подписи вместо кодов. */
  options?: SelectOption[]
}

export interface CrudField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'money' | 'select' | 'date' | 'checkbox' | 'color'
  required?: boolean
  placeholder?: string
  maxlength?: number
  min?: number
  max?: number
  hint?: string
  options?: SelectOption[]
  /** Зависимые списки: набор вариантов считается от текущих значений формы. */
  optionsFor?: (form: FormValues) => SelectOption[]
  /** Имя поля, при изменении которого это поле сбрасывается. */
  resetOn?: string
  defaultValue?: unknown
  /** Поле нельзя менять после создания записи. */
  disabledOnEdit?: boolean
}
