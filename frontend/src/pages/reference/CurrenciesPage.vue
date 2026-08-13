<script setup lang="ts">
import { currenciesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import type { CrudColumn, CrudField } from '@/types/crud'

const columns: CrudColumn[] = [
  { field: 'code', header: 'Код', width: '7rem' },
  { field: 'name', header: 'Название', sortable: true },
  { field: 'symbol', header: 'Символ', width: '7rem' },
  { field: 'minor_unit', header: 'Знаков', width: '7rem' },
  { field: 'is_active', header: 'Активна', type: 'boolean', width: '8rem' },
]

const fields: CrudField[] = [
  {
    name: 'code',
    label: 'Код ISO 4217',
    type: 'text',
    required: true,
    maxlength: 3,
    placeholder: 'RUB',
  },
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 64 },
  { name: 'symbol', label: 'Символ', type: 'text', required: true, maxlength: 16 },
  {
    name: 'minor_unit',
    label: 'Знаков после запятой',
    type: 'number',
    required: true,
    min: 0,
    max: 4,
    defaultValue: 2,
    hint: 'Две — для рубля и доллара, ноль — для иены',
  },
  { name: 'is_active', label: 'Активна', type: 'checkbox', defaultValue: true },
]
</script>

<template>
  <ReferenceCrud
    title="Валюты"
    icon="pi pi-dollar"
    subtitle="Валюты расчётов и число знаков после запятой"
    entity-accusative="валюту"
    search-placeholder="Код или название"
    title-field="code"
    :api="currenciesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
