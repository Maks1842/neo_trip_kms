<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { accommodationsApi, citiesApi, countriesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import { useNotify } from '@/composables/useNotify'
import type { City } from '@/types/reference'
import type { CrudColumn, CrudField, FormValues, SelectOption } from '@/types/crud'

const notify = useNotify()
const countries = ref<SelectOption[]>([])
const cities = ref<City[]>([])

const TYPES: SelectOption[] = [
  { label: 'Отель', value: 'hotel' },
  { label: 'Санаторий', value: 'sanatorium' },
]

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'type', header: 'Тип', type: 'options', options: TYPES, width: '10rem' },
  { field: 'city_id', header: 'Город', type: 'options', options: [] },
  { field: 'rating', header: 'Рейтинг', width: '8rem' },
  { field: 'is_active', header: 'Активен', type: 'boolean', width: '8rem' },
]

const fields: CrudField[] = [
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 255 },
  { name: 'type', label: 'Тип', type: 'select', required: true, options: TYPES },
  {
    name: 'country_id',
    label: 'Страна',
    type: 'select',
    required: true,
    optionsFor: () => countries.value,
  },
  {
    name: 'city_id',
    label: 'Город',
    type: 'select',
    required: true,
    // Список городов зависит от выбранной страны: сервер не примет пару,
    // в которой город относится к другой стране.
    optionsFor: (form: FormValues) =>
      cities.value
        .filter((city) => !form.country_id || city.country_id === form.country_id)
        .map((city) => ({ label: city.name, value: city.id })),
    resetOn: 'country_id',
  },
  { name: 'address', label: 'Адрес', type: 'text', maxlength: 255 },
  { name: 'description', label: 'Описание', type: 'textarea' },
  { name: 'rating', label: 'Рейтинг', type: 'money', min: 0, max: 10, hint: 'От 0 до 10' },
  { name: 'is_active', label: 'Активен в продаже', type: 'checkbox', defaultValue: true },
]

onMounted(async () => {
  try {
    const [countryPage, cityPage] = await Promise.all([
      countriesApi.list({ limit: 200 }),
      citiesApi.list({ limit: 500 }),
    ])
    countries.value = countryPage.items.map((item) => ({ label: item.name, value: item.id }))
    cities.value = cityPage.items
    columns[2].options = cityPage.items.map((item) => ({ label: item.name, value: item.id }))
  } catch (error) {
    notify.apiError(error, 'Не удалось загрузить справочники')
  }
})
</script>

<template>
  <ReferenceCrud
    title="Объекты размещения"
    icon="pi pi-building"
    subtitle="Отели и санатории — справочник и прайс, без номерного фонда"
    entity-accusative="объект размещения"
    search-placeholder="Название объекта"
    :api="accommodationsApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
