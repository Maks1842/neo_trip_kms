"""Сборка роутеров справочников."""

from fastapi import APIRouter

from app.reference.accommodations.router import programs_router
from app.reference.accommodations.router import router as accommodations_router
from app.reference.cities.router import router as cities_router
from app.reference.countries.router import router as countries_router
from app.reference.currencies.router import router as currencies_router
from app.reference.deal_stages.router import custom_router as deal_stages_custom_router
from app.reference.deal_stages.router import router as deal_stages_router
from app.reference.document_templates.router import router as document_templates_router
from app.reference.partners.router import router as partners_router
from app.reference.tariff_entries.router import router as tariff_entries_router

reference_router = APIRouter(prefix="/reference")

# Роутер с нестандартными путями подключается раньше типового CRUD, иначе
# конкретные маршруты перехватит шаблон /{item_id}.
reference_router.include_router(deal_stages_custom_router)

reference_router.include_router(countries_router)
reference_router.include_router(cities_router)
reference_router.include_router(currencies_router)
reference_router.include_router(accommodations_router)
reference_router.include_router(programs_router)
reference_router.include_router(tariff_entries_router)
reference_router.include_router(deal_stages_router)
reference_router.include_router(partners_router)
reference_router.include_router(document_templates_router)
