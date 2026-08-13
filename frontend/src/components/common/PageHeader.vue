<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
  icon?: string
}

defineProps<Props>()
</script>

<template>
  <div class="page__header">
    <div>
      <h1 class="page__title">
        <i v-if="icon" :class="icon" style="color: var(--p-primary-color)" />
        {{ title }}
      </h1>
      <p v-if="subtitle" class="page__subtitle">{{ subtitle }}</p>
    </div>
    <div class="page__actions">
      <slot name="actions" />
    </div>
  </div>
</template>
