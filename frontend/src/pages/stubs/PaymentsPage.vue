<script setup lang="ts">
import PageStub from '@/components/common/PageStub.vue'
</script>

<template>
  <PageStub
    title="Платежи"
    icon="pi pi-wallet"
    description="Фактическое движение денег по сделкам."
    :planned-features="[
      'Поступления и возвраты',
      'Сверка с эквайрингом и учётной системой',
      'Связь платежа со сделкой и её позициями'
    ]"
  />
</template>
