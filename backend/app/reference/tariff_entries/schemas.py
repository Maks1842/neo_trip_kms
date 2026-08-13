"""Схемы справочника тарифов."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field, model_validator
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.reference.tariff_entries.models import TariffEntry


class TariffEntryCreate(BaseSchema):
    accommodation_id: UUID
    program_id: UUID
    season_start: date
    season_end: date
    # Цена приходит в основных единицах (рублях); перевод в копейки делает сервис.
    price: Decimal = Field(ge=0, decimal_places=4)
    currency_id: UUID
    occupancy_config: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_season(self) -> "TariffEntryCreate":
        if self.season_start > self.season_end:
            raise ValueError("Начало сезона не может быть позже его окончания")
        return self


class TariffEntryUpdate(BaseSchema):
    accommodation_id: UUID | None = None
    program_id: UUID | None = None
    season_start: date | None = None
    season_end: date | None = None
    price: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    currency_id: UUID | None = None
    occupancy_config: dict[str, Any] | None = None

    @model_validator(mode="after")
    def check_season(self) -> "TariffEntryUpdate":
        if (
            self.season_start is not None
            and self.season_end is not None
            and self.season_start > self.season_end
        ):
            raise ValueError("Начало сезона не может быть позже его окончания")
        return self


class TariffEntryRead(IdSchema, TimestampSchema):
    accommodation_id: UUID
    program_id: UUID
    season_start: date
    season_end: date
    # Значения вычисляются моделью из price_minor и minor_unit валюты.
    price: Decimal
    currency_id: UUID
    currency_code: str
    occupancy_config: dict[str, Any]


class TariffEntryFilter(BaseFilter):
    accommodation_id: UUID | None = None
    program_id: UUID | None = None
    active_on: date | None = Field(default=None, description="Тарифы, действующие на дату")

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.accommodation_id is not None:
            conditions.append(TariffEntry.accommodation_id == self.accommodation_id)
        if self.program_id is not None:
            conditions.append(TariffEntry.program_id == self.program_id)
        if self.active_on is not None:
            conditions.append(TariffEntry.season_start <= self.active_on)
            conditions.append(TariffEntry.season_end >= self.active_on)
        return conditions
