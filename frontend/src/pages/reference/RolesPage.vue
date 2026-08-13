<script setup lang="ts">
import { rolesApi } from '@/api/reference'
import ReferenceCrud from '@/components/common/ReferenceCrud.vue'
import type { CrudColumn, CrudField } from '@/types/crud'

const columns: CrudColumn[] = [
  { field: 'name', header: 'Название', sortable: true },
  { field: 'is_system', header: 'Системная', type: 'boolean', width: '10rem' },
]

// Права редактируются на отдельном экране: плоский список кодов в текстовом поле
// был бы источником опечаток, а сервер отклоняет неизвестные коды.
const fields: CrudField[] = [
  { name: 'name', label: 'Название роли', type: 'text', required: true, maxlength: 120 },
]
</script>

<template>
  <ReferenceCrud
    title="Роли"
    icon="pi pi-lock"
    subtitle="Наборы прав сотрудников. Системные роли изменять нельзя"
    entity-accusative="роль"
    search-placeholder="Название роли"
    manage-permission="roles.manage"
    :api="rolesApi as never"
    :columns="columns"
    :fields="fields"
  />
</template>
