<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Лиды"
    icon="pi pi-inbox"
    description="Входящие заявки в исходном виде: то, что клиент реально написал, без нормализации."
    :planned-features="[
      'Приём заявок из внешних источников',
      'Поиск и связывание дублей',
      'Возврат просроченной заявки в общий сток',
      'Конвертация лида в клиента и сделку'
    ]"
  />
</template>
