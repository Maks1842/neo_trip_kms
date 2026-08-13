<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { citiesApi, countriesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import { useNotify } from '@/composables/useNotify'
import type { CrudColumn, CrudField, SelectOption } from '@/types/crud'

const notify = useNotify()
const countries = ref<SelectOption[]>([])

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'country_id', header: 'Страна', type: 'options', options: [] },
]

const fields: CrudField[] = [
  {
    name: 'country_id',
    label: 'Страна',
    type: 'select',
    required: true,
    optionsFor: () => countries.value,
  },
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 120 },
]

onMounted(async () => {
  try {
    // Полный список стран нужен и для формы, и для подписей в таблице.
    const data = await countriesApi.list({ limit: 200 })
    countries.value = data.items.map((item) => ({ label: item.name, value: item.id }))
    columns[1].options = countries.value
  } catch (error) {
    notify.apiError(error, 'Не удалось загрузить список стран')
  }
})
</script>

<template>
  <ReferenceCrud
    title="Города"
    icon="pi pi-map-marker"
    subtitle="Города направлений, привязанные к странам"
    entity-accusative="город"
    search-placeholder="Название города"
    :api="citiesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
