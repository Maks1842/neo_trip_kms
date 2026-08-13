"""Схемы справочника объектов размещения и программ."""

from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from pydantic import Field
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.db.enums import AccommodationType
from app.reference.accommodations.models import Accommodation, AccommodationProgram


class AccommodationCreate(BaseSchema):
    name: str = Field(max_length=255)
    type: AccommodationType
    country_id: UUID
    city_id: UUID
    address: str | None = Field(default=None, max_length=255)
    description: str | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=10)
    is_active: bool = True


class AccommodationUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    type: AccommodationType | None = None
    country_id: UUID | None = None
    city_id: UUID | None = None
    address: str | None = Field(default=None, max_length=255)
    description: str | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=10)
    is_active: bool | None = None


class AccommodationRead(IdSchema, TimestampSchema):
    name: str
    type: AccommodationType
    country_id: UUID
    city_id: UUID
    address: str | None
    description: str | None
    rating: Decimal | None
    is_active: bool


class AccommodationFilter(BaseFilter):
    search: str | None = None
    type: AccommodationType | None = None
    country_id: UUID | None = None
    city_id: UUID | None = None
    is_active: bool | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.search:
            conditions.append(Accommodation.name.ilike(f"%{self.search}%"))
        if self.type is not None:
            conditions.append(Accommodation.type == self.type)
        if self.country_id is not None:
            conditions.append(Accommodation.country_id == self.country_id)
        if self.city_id is not None:
            conditions.append(Accommodation.city_id == self.city_id)
        if self.is_active is not None:
            conditions.append(Accommodation.is_active.is_(self.is_active))
        return conditions


# ---------- Программы размещения ----------


class AccommodationProgramCreate(BaseSchema):
    accommodation_id: UUID
    name: str = Field(max_length=255)
    capacity: int = Field(default=1, ge=1, le=50)
    description: str | None = None
    is_active: bool = True


class AccommodationProgramUpdate(BaseSchema):
    accommodation_id: UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    capacity: int | None = Field(default=None, ge=1, le=50)
    description: str | None = None
    is_active: bool | None = None


class AccommodationProgramRead(IdSchema, TimestampSchema):
    accommodation_id: UUID
    name: str
    capacity: int
    description: str | None
    is_active: bool


class AccommodationProgramFilter(BaseFilter):
    accommodation_id: UUID | None = None
    search: str | None = None
    is_active: bool | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.accommodation_id is not None:
            conditions.append(AccommodationProgram.accommodation_id == self.accommodation_id)
        if self.search:
            conditions.append(AccommodationProgram.name.ilike(f"%{self.search}%"))
        if self.is_active is not None:
            conditions.append(AccommodationProgram.is_active.is_(self.is_active))
        return conditions
