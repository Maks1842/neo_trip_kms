"""Роутер справочника стран."""

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError
from app.reference.cities.models import City
from app.reference.countries.models import Country
from app.reference.countries.schemas import (
    CountryCreate,
    CountryFilter,
    CountryRead,
    CountryUpdate,
)


class CountryService(CRUDService[Country, CountryCreate, CountryUpdate]):
    model = Country
    # Страны общие для всех компаний, поэтому фильтр по тенанту не применяется.
    tenant_scoped = False
    default_order_by = ("name",)
    unique_fields = (("code",), ("name",))
    entity_name = "Страна"

    async def _check_delete(self, obj: Country) -> None:
        # Внешний ключ городов настроен на RESTRICT, но понятное сообщение
        # лучше, чем ошибка драйвера.
        stmt = select(City.id).where(City.country_id == obj.id).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Нельзя удалить страну, к которой привязаны города")


router = build_crud_router(
    service_class=CountryService,
    prefix="/countries",
    tags=["Справочники: страны"],
    read_schema=CountryRead,
    create_schema=CountryCreate,
    update_schema=CountryUpdate,
    filter_schema=CountryFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="countries",
)
