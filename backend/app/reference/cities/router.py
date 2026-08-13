"""Роутер справочника городов."""

from typing import Any

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import BusinessValidationError
from app.reference.cities.models import City
from app.reference.cities.schemas import CityCreate, CityFilter, CityRead, CityUpdate
from app.reference.countries.models import Country


class CityService(CRUDService[City, CityCreate, CityUpdate]):
    model = City
    tenant_scoped = False
    default_order_by = ("name",)
    unique_fields = (("country_id", "name"),)
    entity_name = "Город"

    async def _ensure_country_exists(self, values: dict[str, Any]) -> None:
        country_id = values.get("country_id")
        if country_id is None:
            return
        stmt = select(Country.id).where(Country.id == country_id)
        if (await self.session.execute(stmt)).scalar_one_or_none() is None:
            raise BusinessValidationError("Указанная страна не найдена")

    async def _prepare_create(self, values: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_country_exists(values)
        return values

    async def _prepare_update(self, obj: City, values: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_country_exists(values)
        return values


router = build_crud_router(
    service_class=CityService,
    prefix="/cities",
    tags=["Справочники: города"],
    read_schema=CityRead,
    create_schema=CityCreate,
    update_schema=CityUpdate,
    filter_schema=CityFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="cities",
)
