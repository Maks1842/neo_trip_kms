<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Настройки"
    icon="pi pi-cog"
    description="Параметры компании, оформление и управление пользователями."
    :planned-features="[
      'Профиль компании',
      'Оформление интерфейса под бренд агентства',
      'Пользователи и назначение ролей'
    ]"
  />
</template>
