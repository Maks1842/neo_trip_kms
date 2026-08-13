<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Коммуникации"
    icon="pi pi-comments"
    description="Единая лента переписки с клиентом по всем каналам."
    :planned-features="[
      'Лента сообщений WhatsApp, Telegram и почты',
      'Журнал звонков с записями',
      'Транскрибация и краткое содержание разговора'
    ]"
  />
</template>
