"""Роутер справочника тарифов."""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.money import to_minor
from app.common.service import CRUDService
from app.core.exceptions import BusinessValidationError, ConflictError
from app.reference.accommodations.models import Accommodation, AccommodationProgram
from app.reference.currencies.models import Currency
from app.reference.tariff_entries.models import TariffEntry
from app.reference.tariff_entries.schemas import (
    TariffEntryCreate,
    TariffEntryFilter,
    TariffEntryRead,
    TariffEntryUpdate,
)


class TariffEntryService(CRUDService[TariffEntry, TariffEntryCreate, TariffEntryUpdate]):
    model = TariffEntry
    default_order_by = ("season_start",)
    entity_name = "Тариф"

    async def _convert_price(self, values: dict[str, Any]) -> None:
        """Переводит цену из рублей в копейки по числу знаков валюты."""
        if "price" not in values:
            return
        currency_id = values.get("currency_id")
        if currency_id is None:
            raise BusinessValidationError("Для изменения цены нужно указать валюту")

        stmt = select(Currency).where(Currency.id == currency_id, Currency.is_active.is_(True))
        currency = (await self.session.execute(stmt)).scalar_one_or_none()
        if currency is None:
            raise BusinessValidationError("Валюта не найдена или неактивна")

        price: Decimal = values.pop("price")
        values["price_minor"] = to_minor(price, currency.minor_unit)

    async def _validate_parents(self, values: dict[str, Any], obj: TariffEntry | None) -> None:
        accommodation_id = values.get("accommodation_id") or (obj.accommodation_id if obj else None)
        program_id = values.get("program_id") or (obj.program_id if obj else None)
        if accommodation_id is None or program_id is None:
            return

        stmt = select(Accommodation.id).where(
            Accommodation.id == accommodation_id,
            Accommodation.company_id == self.actor.company_id,
        )
        if (await self.session.execute(stmt)).scalar_one_or_none() is None:
            raise BusinessValidationError("Объект размещения не найден")

        # Программа обязана принадлежать указанному объекту, иначе тариф
        # окажется привязан к чужому номеру.
        stmt_program = select(AccommodationProgram.accommodation_id).where(
            AccommodationProgram.id == program_id
        )
        program_parent = (await self.session.execute(stmt_program)).scalar_one_or_none()
        if program_parent is None:
            raise BusinessValidationError("Программа размещения не найдена")
        if program_parent != accommodation_id:
            raise BusinessValidationError("Программа не относится к указанному объекту размещения")

    async def _check_season_overlap(
        self,
        values: dict[str, Any],
        obj: TariffEntry | None,
    ) -> None:
        """Сезоны одного тарифа не должны пересекаться.

        Иначе калькулятор цены получил бы два тарифа на одну дату и не смог бы
        выбрать между ними.
        """
        program_id: UUID | None = values.get("program_id") or (obj.program_id if obj else None)
        season_start: date | None = values.get("season_start") or (
            obj.season_start if obj else None
        )
        season_end: date | None = values.get("season_end") or (obj.season_end if obj else None)
        if program_id is None or season_start is None or season_end is None:
            return
        if season_start > season_end:
            raise BusinessValidationError("Начало сезона не может быть позже его окончания")

        conditions = [
            TariffEntry.program_id == program_id,
            TariffEntry.company_id == self.actor.company_id,
            # Пересечение отрезков: начало одного не позже конца другого и наоборот.
            and_(TariffEntry.season_start <= season_end, TariffEntry.season_end >= season_start),
        ]
        if obj is not None:
            conditions.append(TariffEntry.id != obj.id)

        stmt = select(TariffEntry.id).where(*conditions).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Для этой программы уже есть тариф на пересекающийся период")

    async def _prepare_create(self, values: dict[str, Any]) -> dict[str, Any]:
        await self._validate_parents(values, None)
        await self._check_season_overlap(values, None)
        await self._convert_price(values)
        return values

    async def _prepare_update(self, obj: TariffEntry, values: dict[str, Any]) -> dict[str, Any]:
        await self._validate_parents(values, obj)
        await self._check_season_overlap(values, obj)
        if "price" in values and "currency_id" not in values:
            # При частичном обновлении валюта может не приходить — берём текущую.
            values["currency_id"] = obj.currency_id
            await self._convert_price(values)
            values.pop("currency_id", None)
        else:
            await self._convert_price(values)
        return values


router = build_crud_router(
    service_class=TariffEntryService,
    prefix="/tariff-entries",
    tags=["Справочники: тарифы"],
    read_schema=TariffEntryRead,
    create_schema=TariffEntryCreate,
    update_schema=TariffEntryUpdate,
    filter_schema=TariffEntryFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="tariff_entries",
)
