/** Типы справочников. */

import type { BaseEntity } from '@/types/api'

export type AccommodationType = 'hotel' | 'sanatorium'
export type FunnelType = 'cruise' | 'tour' | 'sanatorium'
export type PartnerType = 'sub_agent' | 'referral_client' | 'affiliate'
export type DocumentType = 'contract' | 'invoice' | 'voucher'

// ---------- Страны ----------

export interface Country extends BaseEntity {
  name: string
  code: string
}

export interface CountryPayload {
  name: string
  code: string
}

// ---------- Города ----------

export interface City extends BaseEntity {
  name: string
  country_id: string
}

export interface CityPayload {
  name: string
  country_id: string
}

// ---------- Валюты ----------

export interface Currency extends BaseEntity {
  code: string
  name: string
  symbol: string
  minor_unit: number
  is_active: boolean
}

export interface CurrencyPayload {
  code: string
  name: string
  symbol: string
  minor_unit: number
  is_active: boolean
}

// ---------- Объекты размещения ----------

export interface Accommodation extends BaseEntity {
  name: string
  type: AccommodationType
  country_id: string
  city_id: string
  address: string | null
  description: string | null
  rating: string | null
  is_active: boolean
}

export interface AccommodationPayload {
  name: string
  type: AccommodationType
  country_id: string
  city_id: string
  address?: string | null
  description?: string | null
  rating?: number | null
  is_active?: boolean
}

// ---------- Программы размещения ----------

export interface AccommodationProgram extends BaseEntity {
  accommodation_id: string
  name: string
  capacity: number
  description: string | null
  is_active: boolean
}

export interface AccommodationProgramPayload {
  accommodation_id: string
  name: string
  capacity: number
  description?: string | null
  is_active?: boolean
}

// ---------- Тарифы ----------

export interface TariffEntry extends BaseEntity {
  accommodation_id: string
  program_id: string
  season_start: string
  season_end: string
  /** Цена в основных единицах валюты: в копейки её переводит backend. */
  price: string
  currency_id: string
  currency_code: string
  occupancy_config: Record<string, unknown>
}

export interface TariffEntryPayload {
  accommodation_id: string
  program_id: string
  season_start: string
  season_end: string
  price: number
  currency_id: string
  occupancy_config?: Record<string, unknown>
}

// ---------- Этапы воронок ----------

export interface DealStage extends BaseEntity {
  funnel_type: FunnelType
  name: string
  sort_order: number
  color_hex: string
  sla_hours: number | null
}

export interface DealStagePayload {
  funnel_type: FunnelType
  name: string
  sort_order?: number
  color_hex?: string
  sla_hours?: number | null
}

// ---------- Партнёры ----------

export interface Partner extends BaseEntity {
  name: string
  type: PartnerType
  contact_phone: string | null
  contact_email: string | null
  commission_percent: string | null
  is_active: boolean
}

export interface PartnerPayload {
  name: string
  type: PartnerType
  contact_phone?: string | null
  contact_email?: string | null
  commission_percent?: number | null
  is_active?: boolean
}

// ---------- Шаблоны документов ----------

export interface DocumentTemplate extends BaseEntity {
  name: string
  type: DocumentType
  accommodation_id: string | null
  template_body: string
  is_active: boolean
}

export interface DocumentTemplatePayload {
  name: string
  type: DocumentType
  accommodation_id?: string | null
  template_body: string
  is_active?: boolean
}

// ---------- Роли ----------

export interface Role extends BaseEntity {
  name: string
  permissions: string[]
  is_system: boolean
}

export interface RolePayload {
  name: string
  permissions: string[]
}
