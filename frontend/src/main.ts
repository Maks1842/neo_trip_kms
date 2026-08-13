import Aura from '@primeuix/themes/aura'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import { createApp } from 'vue'

import App from '@/App.vue'
import { setupInterceptors } from '@/api/client'
import router from '@/router'

import 'primeicons/primeicons.css'
import '@/assets/styles/main.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      // Тёмная тема включается классом, а не системной настройкой: выбор
      // пользователя должен сохраняться между сессиями.
      darkModeSelector: '.app-dark',
      cssLayer: false,
    },
  },
  locale: {
    accept: 'Да',
    reject: 'Нет',
    cancel: 'Отмена',
    clear: 'Очистить',
    apply: 'Применить',
    emptyMessage: 'Ничего не найдено',
    emptySearchMessage: 'Совпадений нет',
    emptySelectionMessage: 'Ничего не выбрано',
  },
})
app.use(ToastService)
app.use(ConfirmationService)
app.directive('tooltip', Tooltip)

// Перехватчики подключаются после Pinia: они обращаются к стору авторизации.
setupInterceptors()

app.mount('#app')
