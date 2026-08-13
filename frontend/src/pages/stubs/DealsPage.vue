<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Сделки"
    icon="pi pi-briefcase"
    description="Канбан-доска по воронкам: круизы, туры, санатории."
    :planned-features="[
      'Канбан с этапами воронки',
      'Карточка сделки в боковой панели',
      'Позиции сделки с себестоимостью и маржой',
      'Туристы со слепком паспортных данных'
    ]"
  />
</template>
