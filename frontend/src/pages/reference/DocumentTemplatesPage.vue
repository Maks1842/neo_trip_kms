<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { accommodationsApi, documentTemplatesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import { useNotify } from '@/composables/useNotify'
import type { CrudColumn, CrudField, SelectOption } from '@/types/crud'

const notify = useNotify()
const accommodations = ref<SelectOption[]>([])

const TYPES: SelectOption[] = [
  { label: 'Договор', value: 'contract' },
  { label: 'Счёт', value: 'invoice' },
  { label: 'Ваучер', value: 'voucher' },
]

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'type', header: 'Тип', type: 'options', options: TYPES, width: '11rem' },
  { field: 'accommodation_id', header: 'Объект', type: 'options', options: [] },
  { field: 'is_active', header: 'Активен', type: 'boolean', width: '8rem' },
]

const fields: CrudField[] = [
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 255 },
  { name: 'type', label: 'Тип документа', type: 'select', required: true, options: TYPES },
  {
    name: 'accommodation_id',
    label: 'Объект размещения',
    type: 'select',
    optionsFor: () => accommodations.value,
    hint: 'Заполняется, если у отеля своя форма бланка',
  },
  {
    name: 'template_body',
    label: 'Тело шаблона',
    type: 'textarea',
    required: true,
    hint: 'Текст с плейсхолдерами для подстановки данных сделки',
  },
  { name: 'is_active', label: 'Активен', type: 'checkbox', defaultValue: true },
]

onMounted(async () => {
  try {
    const data = await accommodationsApi.list({ limit: 500 })
    accommodations.value = data.items.map((item) => ({ label: item.name, value: item.id }))
    columns[2].options = accommodations.value
  } catch (error) {
    notify.apiError(error, 'Не удалось загрузить объекты размещения')
  }
})
</script>

<template>
  <ReferenceCrud
    title="Шаблоны документов"
    icon="pi pi-copy"
    subtitle="Формы договоров, счетов и ваучеров"
    entity-accusative="шаблон"
    search-placeholder="Название шаблона"
    :api="documentTemplatesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
