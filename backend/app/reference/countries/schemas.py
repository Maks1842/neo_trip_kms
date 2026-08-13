"""Схемы справочника стран."""

from collections.abc import Sequence

from pydantic import Field, field_validator
from sqlalchemy import ColumnElement, or_

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.reference.countries.models import Country


class CountryCreate(BaseSchema):
    name: str = Field(max_length=120)
    code: str = Field(min_length=2, max_length=2, description="Код ISO 3166-1 alpha-2")

    @field_validator("code")
    @classmethod
    def upper_code(cls, value: str) -> str:
        return value.upper()


class CountryUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=120)
    code: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("code")
    @classmethod
    def upper_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class CountryRead(IdSchema, TimestampSchema):
    name: str
    code: str


class CountryFilter(BaseFilter):
    search: str | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        if not self.search:
            return []
        pattern = f"%{self.search}%"
        return [or_(Country.name.ilike(pattern), Country.code.ilike(pattern))]
