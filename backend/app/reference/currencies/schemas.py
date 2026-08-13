"""Схемы справочника валют."""

from collections.abc import Sequence

from pydantic import Field, field_validator
from sqlalchemy import ColumnElement, or_

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.reference.currencies.models import Currency


class CurrencyCreate(BaseSchema):
    code: str = Field(min_length=3, max_length=3, description="Код ISO 4217, например RUB")
    name: str = Field(max_length=64)
    symbol: str = Field(max_length=16)
    minor_unit: int = Field(default=2, ge=0, le=4, description="Знаков после запятой")
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def upper_code(cls, value: str) -> str:
        return value.upper()


class CurrencyUpdate(BaseSchema):
    code: str | None = Field(default=None, min_length=3, max_length=3)
    name: str | None = Field(default=None, max_length=64)
    symbol: str | None = Field(default=None, max_length=16)
    minor_unit: int | None = Field(default=None, ge=0, le=4)
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def upper_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class CurrencyRead(IdSchema, TimestampSchema):
    code: str
    name: str
    symbol: str
    minor_unit: int
    is_active: bool


class CurrencyFilter(BaseFilter):
    search: str | None = None
    is_active: bool | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.search:
            pattern = f"%{self.search}%"
            conditions.append(or_(Currency.code.ilike(pattern), Currency.name.ilike(pattern)))
        if self.is_active is not None:
            conditions.append(Currency.is_active.is_(self.is_active))
        return conditions
