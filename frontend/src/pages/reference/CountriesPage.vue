<script setup lang="ts">
import { countriesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import type { CrudColumn, CrudField } from '@/types/crud'

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'code', header: 'Код', width: '8rem' },
]

const fields: CrudField[] = [
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 120 },
  {
    name: 'code',
    label: 'Код ISO 3166-1',
    type: 'text',
    required: true,
    maxlength: 2,
    placeholder: 'RU',
    hint: 'Две заглавные латинские буквы',
  },
]
</script>

<template>
  <ReferenceCrud
    title="Страны"
    icon="pi pi-globe"
    subtitle="Общий справочник направлений для всех компаний"
    entity-accusative="страну"
    search-placeholder="Название или код"
    :api="countriesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
