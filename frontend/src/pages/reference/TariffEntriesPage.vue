<script setup lang="ts">
import { onMounted, ref } from 'vue'

import {
  accommodationProgramsApi,
  accommodationsApi,
  currenciesApi,
  tariffEntriesApi,
} from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import { useNotify } from '@/composables/useNotify'
import type { AccommodationProgram } from '@/types/reference'
import type { CrudColumn, CrudField, FormValues, SelectOption } from '@/types/crud'

const notify = useNotify()
const accommodations = ref<SelectOption[]>([])
const programs = ref<AccommodationProgram[]>([])
const currencies = ref<SelectOption[]>([])

const columns: CrudColumn[] = [
  { field: 'accommodation_id', header: 'Объект', type: 'options', options: [] },
  { field: 'program_id', header: 'Программа', type: 'options', options: [] },
  { field: 'season_start', header: 'Начало сезона', width: '11rem' },
  { field: 'season_end', header: 'Конец сезона', width: '11rem' },
  { field: 'price', header: 'Цена', width: '10rem' },
  { field: 'currency_code', header: 'Валюта', width: '7rem' },
]

const fields: CrudField[] = [
  {
    name: 'accommodation_id',
    label: 'Объект размещения',
    type: 'select',
    required: true,
    optionsFor: () => accommodations.value,
  },
  {
    name: 'program_id',
    label: 'Программа',
    type: 'select',
    required: true,
    // Программа обязана принадлежать выбранному объекту — иначе сервер откажет.
    optionsFor: (form: FormValues) =>
      programs.value
        .filter((item) => !form.accommodation_id || item.accommodation_id === form.accommodation_id)
        .map((item) => ({ label: item.name, value: item.id })),
    resetOn: 'accommodation_id',
  },
  { name: 'season_start', label: 'Начало сезона', type: 'date', required: true },
  { name: 'season_end', label: 'Конец сезона', type: 'date', required: true },
  {
    name: 'price',
    label: 'Цена',
    type: 'money',
    required: true,
    min: 0,
    hint: 'Указывается в основных единицах валюты, например в рублях',
  },
  {
    name: 'currency_id',
    label: 'Валюта',
    type: 'select',
    required: true,
    optionsFor: () => currencies.value,
  },
]

onMounted(async () => {
  try {
    const [accPage, progPage, curPage] = await Promise.all([
      accommodationsApi.list({ limit: 500 }),
      accommodationProgramsApi.list({ limit: 500 }),
      currenciesApi.list({ limit: 100 }),
    ])
    accommodations.value = accPage.items.map((item) => ({ label: item.name, value: item.id }))
    programs.value = progPage.items
    currencies.value = curPage.items.map((item) => ({ label: item.code, value: item.id }))
    columns[0].options = accommodations.value
    columns[1].options = progPage.items.map((item) => ({ label: item.name, value: item.id }))
  } catch (error) {
    notify.apiError(error, 'Не удалось загрузить справочники')
  }
})
</script>

<template>
  <ReferenceCrud
    title="Тарифы"
    icon="pi pi-tags"
    subtitle="Сезонные цены программ размещения"
    entity-accusative="тариф"
    search-placeholder="Поиск"
    title-field="season_start"
    :api="tariffEntriesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
