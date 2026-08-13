/**
 * Клиенты справочников.
 *
 * Все ресурсы справочников имеют одинаковый набор операций, поэтому клиент
 * собирается фабрикой — по той же причине, по которой на backend роутеры
 * собираются общей функцией.
 */

import api from '@/api/client'
import type { ListParams, Page } from '@/types/api'
import type {
  Accommodation,
  AccommodationPayload,
  AccommodationProgram,
  AccommodationProgramPayload,
  City,
  CityPayload,
  Country,
  CountryPayload,
  Currency,
  CurrencyPayload,
  DealStage,
  DealStagePayload,
  DocumentTemplate,
  DocumentTemplatePayload,
  Partner,
  PartnerPayload,
  Role,
  RolePayload,
  TariffEntry,
  TariffEntryPayload,
} from '@/types/reference'

export interface CrudApi<TRead, TCreate, TUpdate = Partial<TCreate>> {
  list(params?: ListParams): Promise<Page<TRead>>
  get(id: string): Promise<TRead>
  create(payload: TCreate): Promise<TRead>
  update(id: string, payload: TUpdate): Promise<TRead>
  remove(id: string): Promise<void>
}

export function createCrudApi<TRead, TCreate, TUpdate = Partial<TCreate>>(
  resource: string,
): CrudApi<TRead, TCreate, TUpdate> {
  return {
    async list(params?: ListParams) {
      const { data } = await api.get<Page<TRead>>(`${resource}/`, { params })
      return data
    },
    async get(id: string) {
      const { data } = await api.get<TRead>(`${resource}/${id}`)
      return data
    },
    async create(payload: TCreate) {
      const { data } = await api.post<TRead>(`${resource}/`, payload)
      return data
    },
    async update(id: string, payload: TUpdate) {
      const { data } = await api.patch<TRead>(`${resource}/${id}`, payload)
      return data
    },
    async remove(id: string) {
      await api.delete(`${resource}/${id}`)
    },
  }
}

export const countriesApi = createCrudApi<Country, CountryPayload>('/reference/countries')
export const citiesApi = createCrudApi<City, CityPayload>('/reference/cities')
export const currenciesApi = createCrudApi<Currency, CurrencyPayload>('/reference/currencies')
export const accommodationsApi = createCrudApi<Accommodation, AccommodationPayload>(
  '/reference/accommodations',
)
export const accommodationProgramsApi = createCrudApi<
  AccommodationProgram,
  AccommodationProgramPayload
>('/reference/accommodation-programs')
export const tariffEntriesApi = createCrudApi<TariffEntry, TariffEntryPayload>(
  '/reference/tariff-entries',
)
export const dealStagesApi = createCrudApi<DealStage, DealStagePayload>('/reference/deal-stages')
export const partnersApi = createCrudApi<Partner, PartnerPayload>('/reference/partners')
export const documentTemplatesApi = createCrudApi<DocumentTemplate, DocumentTemplatePayload>(
  '/reference/document-templates',
)
export const rolesApi = createCrudApi<Role, RolePayload>('/roles')

/** Изменение порядка этапов воронки — операция вне общего набора CRUD. */
export async function reorderDealStages(
  items: Array<{ id: string; sort_order: number }>,
): Promise<DealStage[]> {
  const { data } = await api.patch<DealStage[]>('/reference/deal-stages/reorder', { items })
  return data
}
