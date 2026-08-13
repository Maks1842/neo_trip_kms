<script setup lang="ts">
import Message from 'primevue/message'
import { computed } from 'vue'

import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return 'Доброй ночи'
  if (hour < 12) return 'Доброе утро'
  if (hour < 18) return 'Добрый день'
  return 'Добрый вечер'
})

const firstName = computed(() => auth.user?.full_name.split(' ')[0] ?? '')

// Плитки намеренно без чисел: соответствующих эндпоинтов ещё нет, а показывать
// вымышленные показатели в CRM нельзя — по ним начнут принимать решения.
const tiles = [
  { label: 'Сделки в работе', icon: 'pi pi-briefcase' },
  { label: 'Задачи на сегодня', icon: 'pi pi-check-square' },
  { label: 'Новые заявки', icon: 'pi pi-inbox' },
  { label: 'Выручка за месяц', icon: 'pi pi-wallet' },
]
</script>

<template>
  <div class="page">
    <PageHeader
      :title="`${greeting}, ${firstName}`"
      icon="pi pi-home"
      :subtitle="auth.user ? `${auth.user.company.name} · ${auth.user.role.name}` : ''"
    />

    <Message severity="info" :closable="false">
      Показатели появятся после реализации разделов сделок, задач и платежей.
    </Message>

    <div class="form-row">
      <div v-for="tile in tiles" :key="tile.label" class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem">
          <i :class="tile.icon" style="font-size: 1.5rem; color: var(--p-primary-color)" />
          <div>
            <div class="text-muted" style="font-size: 0.85rem">{{ tile.label }}</div>
            <div style="font-size: 1.35rem; font-weight: 600">—</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 style="font-size: 1.05rem; margin-bottom: 0.75rem">Что уже работает</h2>
      <ul class="stub__features">
        <li>Авторизация с обновлением токенов и разграничением прав</li>
        <li>Справочники: страны, города, валюты, объекты размещения, программы, тарифы</li>
        <li>Этапы воронок с изменением порядка, партнёры, шаблоны документов, роли</li>
      </ul>
    </div>
  </div>
</template>
