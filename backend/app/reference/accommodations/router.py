"""Роутеры объектов размещения и программ."""

from typing import Any

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import BusinessValidationError
from app.reference.accommodations.models import Accommodation, AccommodationProgram
from app.reference.accommodations.schemas import (
    AccommodationCreate,
    AccommodationFilter,
    AccommodationProgramCreate,
    AccommodationProgramFilter,
    AccommodationProgramRead,
    AccommodationProgramUpdate,
    AccommodationRead,
    AccommodationUpdate,
)
from app.reference.cities.models import City

PERMISSIONS = CrudPermissions(read="reference.read", write="reference.manage")


class AccommodationService(CRUDService[Accommodation, AccommodationCreate, AccommodationUpdate]):
    model = Accommodation
    default_order_by = ("name",)
    unique_fields = (("name", "city_id"),)
    entity_name = "Объект размещения"

    async def _validate_location(self, values: dict[str, Any], obj: Accommodation | None) -> None:
        """Город должен принадлежать выбранной стране.

        Проверка нужна и при частичном обновлении: клиент может прислать только
        город, оставив страну прежней, и получить несогласованную пару.
        """
        country_id = values.get("country_id") or (obj.country_id if obj else None)
        city_id = values.get("city_id") or (obj.city_id if obj else None)
        if country_id is None or city_id is None:
            return

        stmt = select(City.country_id).where(City.id == city_id)
        actual_country = (await self.session.execute(stmt)).scalar_one_or_none()
        if actual_country is None:
            raise BusinessValidationError("Указанный город не найден")
        if actual_country != country_id:
            raise BusinessValidationError("Город не относится к указанной стране")

    async def _prepare_create(self, values: dict[str, Any]) -> dict[str, Any]:
        await self._validate_location(values, None)
        return values

    async def _prepare_update(self, obj: Accommodation, values: dict[str, Any]) -> dict[str, Any]:
        await self._validate_location(values, obj)
        return values


class AccommodationProgramService(
    CRUDService[AccommodationProgram, AccommodationProgramCreate, AccommodationProgramUpdate]
):
    model = AccommodationProgram
    default_order_by = ("name",)
    unique_fields = (("accommodation_id", "name"),)
    entity_name = "Программа размещения"

    async def _validate_parent(self, values: dict[str, Any]) -> None:
        accommodation_id = values.get("accommodation_id")
        if accommodation_id is None:
            return
        # Родительский объект проверяется с учётом компании: иначе можно было бы
        # привязать свою программу к объекту чужого тенанта.
        stmt = select(Accommodation.id).where(
            Accommodation.id == accommodation_id,
            Accommodation.company_id == self.actor.company_id,
        )
        if (await self.session.execute(stmt)).scalar_one_or_none() is None:
            raise BusinessValidationError("Объект размещения не найден")

    async def _prepare_create(self, values: dict[str, Any]) -> dict[str, Any]:
        await self._validate_parent(values)
        return values

    async def _prepare_update(
        self, obj: AccommodationProgram, values: dict[str, Any]
    ) -> dict[str, Any]:
        await self._validate_parent(values)
        return values


router = build_crud_router(
    service_class=AccommodationService,
    prefix="/accommodations",
    tags=["Справочники: объекты размещения"],
    read_schema=AccommodationRead,
    create_schema=AccommodationCreate,
    update_schema=AccommodationUpdate,
    filter_schema=AccommodationFilter,
    permissions=PERMISSIONS,
    resource_name="accommodations",
)

programs_router = build_crud_router(
    service_class=AccommodationProgramService,
    prefix="/accommodation-programs",
    tags=["Справочники: программы размещения"],
    read_schema=AccommodationProgramRead,
    create_schema=AccommodationProgramCreate,
    update_schema=AccommodationProgramUpdate,
    filter_schema=AccommodationProgramFilter,
    permissions=PERMISSIONS,
    resource_name="accommodation_programs",
)
