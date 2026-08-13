<script setup lang="ts">
import Message from 'primevue/message'

import PageHeader from '@/components/common/PageHeader.vue'

interface Props {
  title: string
  icon: string
  description: string
  /** Что появится в разделе, когда до него дойдёт очередь. */
  plannedFeatures?: string[]
}

defineProps<Props>()
</script>

<template>
  <div class="page">
    <PageHeader :title="title" :icon="icon" :subtitle="description" />

    <div class="card stub">
      <Message severity="info" :closable="false">
        Раздел в разработке: интерфейс появится после реализации серверной части.
      </Message>

      <template v-if="plannedFeatures?.length">
        <p class="text-muted" style="margin: 0">Что здесь будет:</p>
        <ul class="stub__features">
          <li v-for="feature in plannedFeatures" :key="feature">{{ feature }}</li>
        </ul>
      </template>
    </div>
  </div>
</template>
