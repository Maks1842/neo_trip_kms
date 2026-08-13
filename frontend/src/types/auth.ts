/** Типы авторизации. */

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface CompanyBrief {
  id: string
  name: string
  slug: string
}

export interface RoleBrief {
  id: string
  name: string
  permissions: string[]
}

export interface CurrentUser {
  id: string
  full_name: string
  email: string
  phone: string | null
  is_active: boolean
  company: CompanyBrief
  role: RoleBrief
}
