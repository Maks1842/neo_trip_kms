<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { accommodationProgramsApi, accommodationsApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import { useNotify } from '@/composables/useNotify'
import type { CrudColumn, CrudField, SelectOption } from '@/types/crud'

const notify = useNotify()
const accommodations = ref<SelectOption[]>([])

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'accommodation_id', header: 'Объект', type: 'options', options: [] },
  { field: 'capacity', header: 'Вместимость', width: '10rem' },
  { field: 'is_active', header: 'Активна', type: 'boolean', width: '8rem' },
]

const fields: CrudField[] = [
  {
    name: 'accommodation_id',
    label: 'Объект размещения',
    type: 'select',
    required: true,
    optionsFor: () => accommodations.value,
  },
  { name: 'name', label: 'Название программы', type: 'text', required: true, maxlength: 255 },
  {
    name: 'capacity',
    label: 'Вместимость',
    type: 'number',
    required: true,
    min: 1,
    max: 50,
    defaultValue: 2,
    hint: 'Максимальное число туристов',
  },
  { name: 'description', label: 'Описание', type: 'textarea' },
  { name: 'is_active', label: 'Доступна к бронированию', type: 'checkbox', defaultValue: true },
]

onMounted(async () => {
  try {
    const data = await accommodationsApi.list({ limit: 500 })
    accommodations.value = data.items.map((item) => ({ label: item.name, value: item.id }))
    columns[1].options = accommodations.value
  } catch (error) {
    notify.apiError(error, 'Не удалось загрузить объекты размещения')
  }
})
</script>

<template>
  <ReferenceCrud
    title="Программы размещения"
    icon="pi pi-th-large"
    subtitle="Типы номеров и программы внутри объектов"
    entity-accusative="программу"
    search-placeholder="Название программы"
    :api="accommodationProgramsApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
