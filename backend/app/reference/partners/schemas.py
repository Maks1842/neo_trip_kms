"""Схемы справочника партнёров."""

from collections.abc import Sequence
from decimal import Decimal

from pydantic import EmailStr, Field
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.db.enums import PartnerType
from app.reference.partners.models import Partner


class PartnerCreate(BaseSchema):
    name: str = Field(max_length=255)
    type: PartnerType
    contact_phone: str | None = Field(default=None, max_length=32)
    contact_email: EmailStr | None = None
    commission_percent: Decimal | None = Field(default=None, ge=0, le=100)
    is_active: bool = True


class PartnerUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    type: PartnerType | None = None
    contact_phone: str | None = Field(default=None, max_length=32)
    contact_email: EmailStr | None = None
    commission_percent: Decimal | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None


class PartnerRead(IdSchema, TimestampSchema):
    name: str
    type: PartnerType
    contact_phone: str | None
    contact_email: str | None
    commission_percent: Decimal | None
    is_active: bool


class PartnerFilter(BaseFilter):
    search: str | None = None
    type: PartnerType | None = None
    is_active: bool | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.search:
            conditions.append(Partner.name.ilike(f"%{self.search}%"))
        if self.type is not None:
            conditions.append(Partner.type == self.type)
        if self.is_active is not None:
            conditions.append(Partner.is_active.is_(self.is_active))
        return conditions
