<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Задачи"
    icon="pi pi-check-square"
    description="Задачи менеджеров — поставленные вручную и созданные автоматически при смене этапа."
    :planned-features="[
      'Список задач с фильтрами по сроку',
      'Автоматические задачи по этапу воронки',
      'Напоминания о просроченных задачах'
    ]"
  />
</template>
