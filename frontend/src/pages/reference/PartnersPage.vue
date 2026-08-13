<script setup lang="ts">
import { partnersApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import type { CrudColumn, CrudField, SelectOption } from '@/types/crud'

const TYPES: SelectOption[] = [
  { label: 'Субагент', value: 'sub_agent' },
  { label: 'Клиент-реферер', value: 'referral_client' },
  { label: 'Партнёрская сеть', value: 'affiliate' },
]

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'type', header: 'Тип', type: 'options', options: TYPES, width: '13rem' },
  { field: 'contact_phone', header: 'Телефон', width: '12rem' },
  { field: 'contact_email', header: 'Email' },
  { field: 'commission_percent', header: 'Комиссия, %', width: '10rem' },
  { field: 'is_active', header: 'Активен', type: 'boolean', width: '8rem' },
]

const fields: CrudField[] = [
  { name: 'name', label: 'Название', type: 'text', required: true, maxlength: 255 },
  { name: 'type', label: 'Тип партнёра', type: 'select', required: true, options: TYPES },
  { name: 'contact_phone', label: 'Телефон', type: 'text', maxlength: 32 },
  { name: 'contact_email', label: 'Email', type: 'text', maxlength: 255 },
  {
    name: 'commission_percent',
    label: 'Комиссия, %',
    type: 'money',
    min: 0,
    max: 100,
    hint: 'Процент с приведённых сделок',
  },
  { name: 'is_active', label: 'Активен', type: 'checkbox', defaultValue: true },
]
</script>

<template>
  <ReferenceCrud
    title="Партнёры"
    icon="pi pi-id-card"
    subtitle="Субагенты и рефереры, приводящие сделки"
    entity-accusative="партнёра"
    search-placeholder="Название партнёра"
    :api="partnersApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
