<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Документы"
    icon="pi pi-file"
    description="Договоры, счета и ваучеры, сформированные по шаблонам."
    :planned-features="[
      'Генерация документа по сделке',
      'Статусы: черновик, отправлен, подписан',
      'Хранение вложений и сканов'
    ]"
  />
</template>
