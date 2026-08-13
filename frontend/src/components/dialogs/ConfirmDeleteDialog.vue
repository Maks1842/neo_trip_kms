<script setup lang="ts">
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'

interface Props {
  visible: boolean
  itemName?: string
  loading?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: []
}>()
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    header="Удаление записи"
    :style="{ width: '26rem' }"
    @update:visible="emit('update:visible', $event)"
  >
    <p style="margin: 0">
      Удалить <strong>{{ itemName || 'запись' }}</strong>? Действие необратимо.
    </p>

    <template #footer>
      <Button label="Отмена" severity="secondary" text @click="emit('update:visible', false)" />
      <Button label="Удалить" severity="danger" :loading="loading" @click="emit('confirm')" />
    </template>
  </Dialog>
</template>
