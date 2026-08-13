"""Справочник этапов воронок продаж."""

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import FunnelType, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import Str16, Str120


class DealStage(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Этап воронки — статус сделки на канбан-доске."""

    __tablename__ = "deal_stages"
    __table_args__ = (
        # Ограничение отложенное: при перестановке этапов промежуточные состояния
        # временно нарушают уникальность, и без DEFERRABLE операция упала бы на
        # первом же UPDATE.
        UniqueConstraint(
            "company_id",
            "funnel_type",
            "sort_order",
            name="uq_deal_stages_company_id_funnel_type_sort_order",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint("sla_hours IS NULL OR sla_hours > 0", name="sla_hours_positive"),
    )

    funnel_type: Mapped[FunnelType] = mapped_column(pg_enum(FunnelType, "funnel_type"), index=True)
    name: Mapped[Str120]
    # Колонка называется sort_order, а не order: order — зарезервированное слово SQL.
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    color_hex: Mapped[Str16] = mapped_column(default="#6b7280")
    # Лимит времени на этапе. Основа механики авто-возврата просроченной заявки
    # в общий сток.
    sla_hours: Mapped[int | None] = mapped_column(nullable=True)
