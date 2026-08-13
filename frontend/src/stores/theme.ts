/** Стор темы оформления. */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const THEME_KEY = 'neo_trip_theme'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref<boolean>(localStorage.getItem(THEME_KEY) === 'dark')

  // Класс на корневом элементе — тот же селектор, что указан в настройках
  // PrimeVue как darkModeSelector.
  watch(
    isDark,
    (value) => {
      document.documentElement.classList.toggle('app-dark', value)
      localStorage.setItem(THEME_KEY, value ? 'dark' : 'light')
    },
    { immediate: true },
  )

  function toggle(): void {
    isDark.value = !isDark.value
  }

  return { isDark, toggle }
})
