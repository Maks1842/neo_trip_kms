"""Схемы справочника городов."""

from collections.abc import Sequence
from uuid import UUID

from pydantic import Field
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.reference.cities.models import City


class CityCreate(BaseSchema):
    country_id: UUID
    name: str = Field(max_length=120)


class CityUpdate(BaseSchema):
    country_id: UUID | None = None
    name: str | None = Field(default=None, max_length=120)


class CityRead(IdSchema, TimestampSchema):
    country_id: UUID
    name: str


class CityFilter(BaseFilter):
    country_id: UUID | None = None
    search: str | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.country_id is not None:
            conditions.append(City.country_id == self.country_id)
        if self.search:
            conditions.append(City.name.ilike(f"%{self.search}%"))
        return conditions
