"""Схемы справочника этапов воронок."""

from collections.abc import Sequence
from uuid import UUID

from pydantic import Field
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.db.enums import FunnelType
from app.reference.deal_stages.models import DealStage

HEX_COLOR = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"


class DealStageCreate(BaseSchema):
    funnel_type: FunnelType
    name: str = Field(max_length=120)
    sort_order: int = Field(default=0, ge=0)
    color_hex: str = Field(default="#6b7280", pattern=HEX_COLOR)
    sla_hours: int | None = Field(default=None, gt=0, le=8760)


class DealStageUpdate(BaseSchema):
    funnel_type: FunnelType | None = None
    name: str | None = Field(default=None, max_length=120)
    sort_order: int | None = Field(default=None, ge=0)
    color_hex: str | None = Field(default=None, pattern=HEX_COLOR)
    sla_hours: int | None = Field(default=None, gt=0, le=8760)


class DealStageRead(IdSchema, TimestampSchema):
    funnel_type: FunnelType
    name: str
    sort_order: int
    color_hex: str
    sla_hours: int | None


class DealStageFilter(BaseFilter):
    funnel_type: FunnelType | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        if self.funnel_type is None:
            return []
        return [DealStage.funnel_type == self.funnel_type]


class StageOrderItem(BaseSchema):
    id: UUID
    sort_order: int = Field(ge=0)


class ReorderRequest(BaseSchema):
    """Новый порядок этапов внутри одной воронки."""

    items: list[StageOrderItem] = Field(min_length=1)
