<script setup lang="ts">
import { dealStagesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import type { CrudColumn, CrudField, SelectOption } from '@/types/crud'

const FUNNELS: SelectOption[] = [
  { label: 'Туры', value: 'tour' },
  { label: 'Круизы', value: 'cruise' },
  { label: 'Санатории', value: 'sanatorium' },
]

const columns: CrudColumn[] = [
  { field: 'sort_order', header: 'Порядок', width: '8rem', sortable: true },
  { field: 'name', header: 'Название' },
  { field: 'funnel_type', header: 'Воронка', type: 'options', options: FUNNELS, width: '11rem' },
  { field: 'color_hex', header: 'Цвет', type: 'color', width: '6rem' },
  { field: 'sla_hours', header: 'SLA, ч', width: '8rem' },
]

const fields: CrudField[] = [
  { name: 'funnel_type', label: 'Воронка', type: 'select', required: true, options: FUNNELS },
  { name: 'name', label: 'Название этапа', type: 'text', required: true, maxlength: 120 },
  { name: 'sort_order', label: 'Порядок', type: 'number', min: 0, defaultValue: 0 },
  {
    name: 'color_hex',
    label: 'Цвет',
    type: 'color',
    defaultValue: '#6b7280',
    hint: 'Шестнадцатеричный код, например #22c55e',
  },
  {
    name: 'sla_hours',
    label: 'SLA, часов',
    type: 'number',
    min: 1,
    max: 8760,
    hint: 'Через сколько часов простоя заявка возвращается в общий сток',
  },
]
</script>

<template>
  <ReferenceCrud
    title="Этапы воронок"
    icon="pi pi-sitemap"
    subtitle="Статусы сделок на канбан-доске"
    entity-accusative="этап"
    search-placeholder="Название этапа"
    :api="dealStagesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
