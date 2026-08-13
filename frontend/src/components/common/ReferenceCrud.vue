<script setup lang="ts">
/**
 * Экран справочника.
 *
 * Все справочники устроены одинаково: таблица с пагинацией и поиском, диалог
 * формы, подтверждение удаления. Отличаются только колонки и поля, поэтому экран
 * описывается декларативно, а не копируется десять раз с мелкими правками.
 */

import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import DatePicker from 'primevue/datepicker'
import Dialog from 'primevue/dialog'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { onMounted, reactive, watch } from 'vue'

import type { CrudApi } from '@/api/reference'
import PageHeader from '@/components/common/PageHeader.vue'
import ConfirmDeleteDialog from '@/components/dialogs/ConfirmDeleteDialog.vue'
import { useCrud } from '@/composables/useCrud'
import { useAuthStore } from '@/stores/auth'
import type { CrudColumn, CrudField, FormValues } from '@/types/crud'

type Entity = Record<string, unknown> & { id: string }

const props = withDefaults(
  defineProps<{
    title: string
    icon: string
    subtitle?: string
    entityAccusative: string
    /** Поле, по которому запись называется в диалоге удаления. */
    titleField?: string
    api: CrudApi<Entity, FormValues, Partial<FormValues>>
    columns: CrudColumn[]
    fields: CrudField[]
    searchPlaceholder?: string
    managePermission?: string
    extraParams?: () => Record<string, unknown>
  }>(),
  {
    subtitle: undefined,
    titleField: 'name',
    searchPlaceholder: 'Поиск',
    managePermission: 'reference.manage',
    extraParams: undefined,
  },
)

const auth = useAuthStore()
const crud = useCrud<Entity, FormValues, Partial<FormValues>>(props.api, {
  entityAccusative: props.entityAccusative,
  extraParams: props.extraParams,
})

const form = reactive<FormValues>({})

function canManage(): boolean {
  return auth.can(props.managePermission)
}

function defaultsFor(): FormValues {
  const values: FormValues = {}
  for (const field of props.fields) {
    values[field.name] = field.defaultValue ?? (field.type === 'checkbox' ? true : null)
  }
  return values
}

/** Заполняет форму при открытии диалога: создание и редактирование делят её. */
watch(
  () => crud.dialogVisible.value,
  (visible) => {
    if (!visible) return
    const defaults = defaultsFor()
    const source = crud.current.value
    for (const field of props.fields) {
      const raw = source ? source[field.name] : undefined
      if (raw === undefined || raw === null) {
        form[field.name] = defaults[field.name]
      } else if (field.type === 'number' || field.type === 'money') {
        form[field.name] = Number(raw)
      } else if (field.type === 'date') {
        form[field.name] = new Date(String(raw))
      } else {
        form[field.name] = raw as FormValues[string]
      }
    }
  },
)

/** Сброс зависимого поля при смене родительского (страна → город). */
for (const field of props.fields) {
  if (!field.resetOn) continue
  watch(
    () => form[field.resetOn as string],
    () => {
      if (crud.dialogVisible.value) form[field.name] = null
    },
  )
}

function optionsOf(field: CrudField): CrudField['options'] {
  return field.optionsFor ? field.optionsFor(form) : (field.options ?? [])
}

function serialize(): FormValues {
  const payload: FormValues = {}
  for (const field of props.fields) {
    const value = form[field.name]
    if (value === null || value === '') {
      // Пустое необязательное поле отправляем как null, чтобы очистить его.
      payload[field.name] = field.required ? undefined : null
      continue
    }
    if (field.type === 'date' && value instanceof Date) {
      // Дата уходит без времени: на сервере это тип date, а не timestamp.
      payload[field.name] = value.toISOString().slice(0, 10)
    } else {
      payload[field.name] = value
    }
  }
  return payload
}

async function submit(): Promise<void> {
  await crud.save(serialize())
}

function labelOf(column: CrudColumn, value: unknown): string {
  const option = column.options?.find((item) => item.value === value)
  return option?.label ?? String(value ?? '—')
}

onMounted(crud.load)
</script>

<template>
  <div class="page">
    <PageHeader :title="title" :icon="icon" :subtitle="subtitle">
      <template #actions>
        <slot name="actions" />
        <Button v-if="canManage()" label="Добавить" icon="pi pi-plus" @click="crud.openCreate()" />
      </template>
    </PageHeader>

    <slot name="filters" />

    <div class="card card--flush">
      <div class="toolbar" style="padding: 1rem 1rem 0">
        <IconField class="toolbar__search">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="crud.search.value"
            :placeholder="searchPlaceholder"
            class="w-full"
            @input="crud.onSearchInput()"
          />
        </IconField>
      </div>

      <DataTable
        :value="crud.items.value"
        :loading="crud.loading.value"
        lazy
        paginator
        :rows="crud.rows.value"
        :total-records="crud.total.value"
        :rows-per-page-options="[10, 20, 50]"
        data-key="id"
        @page="crud.onPage($event)"
      >
        <template #empty>
          <div class="empty-state">
            <i :class="[icon, 'empty-state__icon']" />
            <span>Записей пока нет</span>
          </div>
        </template>

        <Column
          v-for="column in columns"
          :key="column.field"
          :field="column.field"
          :header="column.header"
          :sortable="column.sortable"
          :style="column.width ? { width: column.width } : undefined"
        >
          <template #body="{ data }">
            <Tag
              v-if="column.type === 'boolean'"
              :value="data[column.field] ? 'Да' : 'Нет'"
              :severity="data[column.field] ? 'success' : 'secondary'"
            />
            <span
              v-else-if="column.type === 'color'"
              :style="{
                display: 'inline-block',
                width: '1.25rem',
                height: '1.25rem',
                borderRadius: '4px',
                background: data[column.field],
              }"
            />
            <span v-else-if="column.type === 'options'">
              {{ labelOf(column, data[column.field]) }}
            </span>
            <span v-else>{{ data[column.field] ?? '—' }}</span>
          </template>
        </Column>

        <Column v-if="canManage()" header="" style="width: 7rem">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.25rem">
              <Button
                icon="pi pi-pencil"
                text
                rounded
                aria-label="Изменить"
                @click="crud.openEdit(data)"
              />
              <Button
                icon="pi pi-trash"
                text
                rounded
                severity="danger"
                aria-label="Удалить"
                @click="crud.confirmDelete(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="crud.dialogVisible.value"
      modal
      :header="crud.current.value ? `Изменение: ${title}` : `Новая запись: ${title}`"
      :style="{ width: '32rem' }"
    >
      <form class="form-grid" @submit.prevent="submit">
        <div v-for="field in fields" :key="field.name" class="form-field">
          <label :for="field.name" class="form-field__label">
            {{ field.label }}<span v-if="field.required"> *</span>
          </label>

          <InputText
            v-if="field.type === 'text'"
            :id="field.name"
            v-model="form[field.name] as string"
            :placeholder="field.placeholder"
            :maxlength="field.maxlength"
          />

          <Textarea
            v-else-if="field.type === 'textarea'"
            :id="field.name"
            v-model="form[field.name] as string"
            rows="4"
            auto-resize
          />

          <InputNumber
            v-else-if="field.type === 'number'"
            :id="field.name"
            v-model="form[field.name] as number"
            :min="field.min"
            :max="field.max"
            show-buttons
          />

          <InputNumber
            v-else-if="field.type === 'money'"
            :id="field.name"
            v-model="form[field.name] as number"
            :min="field.min ?? 0"
            :min-fraction-digits="2"
            :max-fraction-digits="2"
          />

          <Select
            v-else-if="field.type === 'select'"
            :id="field.name"
            v-model="form[field.name] as string"
            :options="optionsOf(field)"
            option-label="label"
            option-value="value"
            :placeholder="field.placeholder ?? 'Выберите значение'"
            :disabled="field.disabledOnEdit && Boolean(crud.current.value)"
            filter
          />

          <DatePicker
            v-else-if="field.type === 'date'"
            :id="field.name"
            v-model="form[field.name] as Date"
            date-format="dd.mm.yy"
            show-icon
          />

          <div v-else-if="field.type === 'checkbox'" style="display: flex; align-items: center">
            <Checkbox :input-id="field.name" v-model="form[field.name] as boolean" binary />
          </div>

          <InputText
            v-else-if="field.type === 'color'"
            :id="field.name"
            v-model="form[field.name] as string"
            placeholder="#6b7280"
          />

          <small v-if="field.hint" class="text-muted">{{ field.hint }}</small>
        </div>
      </form>

      <template #footer>
        <Button
          label="Отмена"
          severity="secondary"
          text
          @click="crud.dialogVisible.value = false"
        />
        <Button label="Сохранить" :loading="crud.saving.value" @click="submit" />
      </template>
    </Dialog>

    <ConfirmDeleteDialog
      v-model:visible="crud.deleteVisible.value"
      :item-name="String(crud.current.value?.[titleField] ?? '')"
      :loading="crud.saving.value"
      @confirm="crud.remove()"
    />
  </div>
</template>
