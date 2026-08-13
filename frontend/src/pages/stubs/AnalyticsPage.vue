<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Аналитика"
    icon="pi pi-chart-bar"
    description="Показатели воронки, выручки и работы менеджеров."
    :planned-features="[
      'Конверсия по этапам воронки',
      'Выручка и маржинальность',
      'Источники заявок и эффективность каналов'
    ]"
  />
</template>
