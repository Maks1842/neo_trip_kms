/** Запросы авторизации. */

import api from '@/api/client'
import type { CurrentUser, TokenPair } from '@/types/auth'

export const authApi = {
  login(email: string, password: string) {
    return api.post<TokenPair>('/auth/login', { email, password })
  },

  refresh(refreshToken: string) {
    return api.post<TokenPair>('/auth/refresh', { refresh_token: refreshToken })
  },

  logout(refreshToken: string) {
    return api.post<void>('/auth/logout', { refresh_token: refreshToken })
  },

  me() {
    return api.get<CurrentUser>('/auth/me')
  },

  changePassword(currentPassword: string, newPassword: string) {
    return api.post<void>('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}
