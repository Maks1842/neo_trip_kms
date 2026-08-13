<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const serverError = ref('')
const loading = ref(false)

function validate(): boolean {
  errors.email = ''
  errors.password = ''

  if (!form.email.trim()) {
    errors.email = 'Укажите email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Похоже, email указан неверно'
  }
  if (!form.password) {
    errors.password = 'Укажите пароль'
  }
  return !errors.email && !errors.password
}

async function submit(): Promise<void> {
  serverError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await auth.login(form.email.trim(), form.password)
    await router.push({ name: 'dashboard' })
  } catch (error) {
    // Ошибка входа показывается в форме, а не всплывающим уведомлением:
    // пользователь в этот момент смотрит именно на форму.
    serverError.value = extractApiError(error, 'Не удалось войти в систему')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-layout">
    <div class="auth-layout__card">
      <div class="auth-layout__brand">
        <i class="pi pi-compass" style="color: var(--p-primary-color)" />
        <span>Neo Trip CRM</span>
      </div>
      <p class="auth-layout__subtitle">Вход в систему</p>

      <form class="form-grid" @submit.prevent="submit">
        <Message v-if="serverError" severity="error" :closable="false">
          {{ serverError }}
        </Message>

        <div class="form-field">
          <label for="email" class="form-field__label">Email</label>
          <InputText
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="username"
            :invalid="Boolean(errors.email)"
            placeholder="admin@neotrip.ru"
          />
          <small v-if="errors.email" class="form-field__error">{{ errors.email }}</small>
        </div>

        <div class="form-field">
          <label for="password" class="form-field__label">Пароль</label>
          <Password
            id="password"
            v-model="form.password"
            input-id="password"
            :feedback="false"
            toggle-mask
            autocomplete="current-password"
            :invalid="Boolean(errors.password)"
            input-class="w-full"
            class="w-full"
          />
          <small v-if="errors.password" class="form-field__error">{{ errors.password }}</small>
        </div>

        <Button type="submit" label="Войти" :loading="loading" class="w-full" />
      </form>
    </div>
  </div>
</template>
