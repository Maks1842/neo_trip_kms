<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Клиенты"
    icon="pi pi-users"
    description="Сквозные карточки клиентов с контактами, предпочтениями и историей."
    :planned-features="[
      'Карточка клиента и его контакты',
      'Защита основного контакта от изменения',
      'Предпочтения и сегментация по тегам',
      'История сделок клиента'
    ]"
  />
</template>
