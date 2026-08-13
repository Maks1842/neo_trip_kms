"""Модели сделки, её позиций и туристов."""

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, false, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import DealItemType, FunnelType, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import (
    JSONBDict,
    LongTextOpt,
    Money,
    MoneyOptional,
    Str32Opt,
    Str64Opt,
    Str255,
    Str255Opt,
)

if TYPE_CHECKING:
    pass


class Deal(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Сделка.

    Все воронки (круизы, туры, санатории) живут в одной таблице и различаются
    полем funnel_type. Специфичные для воронки поля хранятся в extra_fields —
    отдельные таблицы-наследники дали бы три почти одинаковые сущности.
    """

    __tablename__ = "deals"
    __table_args__ = (
        CheckConstraint(
            "date_from IS NULL OR date_to IS NULL OR date_from <= date_to",
            name="date_range_order",
        ),
    )

    funnel_type: Mapped[FunnelType] = mapped_column(pg_enum(FunnelType, "funnel_type"), index=True)
    stage_id: Mapped[UUID] = mapped_column(
        ForeignKey("deal_stages.id", ondelete="RESTRICT"), index=True
    )
    client_id: Mapped[UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    manager_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    partner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("partners.id", ondelete="SET NULL"), nullable=True, index=True
    )
    country_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    city_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"), nullable=True
    )
    # Основной объект размещения для простой сделки. Для пакетной сделки
    # состав услуг описывается позициями DealItem.
    accommodation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accommodations.id", ondelete="SET NULL"), nullable=True
    )

    budget_minor: Mapped[MoneyOptional]
    currency_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"), nullable=True
    )
    date_from: Mapped[date | None] = mapped_column(nullable=True)
    date_to: Mapped[date | None] = mapped_column(nullable=True)

    utm_data: Mapped[JSONBDict]
    extra_fields: Mapped[JSONBDict]

    items: Mapped[list["DealItem"]] = relationship(
        back_populates="deal", lazy="raise", cascade="all, delete-orphan"
    )
    tourists: Mapped[list["Tourist"]] = relationship(
        back_populates="deal", lazy="raise", cascade="all, delete-orphan"
    )


class DealItem(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Позиция сделки: перелёт, проживание, трансфер, экскурсия.

    У каждой позиции свой поставщик, себестоимость и цена продажи — это позволяет
    считать маржу по частям пакета, а не только по сделке целиком.
    """

    __tablename__ = "deal_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("cost_price_minor >= 0", name="cost_price_non_negative"),
        CheckConstraint("sale_price_minor >= 0", name="sale_price_non_negative"),
    )

    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[DealItemType] = mapped_column(pg_enum(DealItemType, "deal_item_type"))
    accommodation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accommodations.id", ondelete="SET NULL"), nullable=True
    )
    supplier_name: Mapped[Str255Opt]
    description: Mapped[LongTextOpt]
    cost_price_minor: Mapped[Money] = mapped_column(default=0, server_default="0")
    sale_price_minor: Mapped[Money] = mapped_column(default=0, server_default="0")
    currency_id: Mapped[UUID] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(default=1, server_default="1", nullable=False)

    deal: Mapped["Deal"] = relationship(back_populates="items", lazy="raise")


class Tourist(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Турист в сделке — слепок паспортных данных на момент оформления.

    Это ключевая идея модели: после создания слепка изменение карточки клиента
    не должно менять уже оформленные документы. Поэтому client_id здесь —
    только ссылка на источник, а не источник истины.
    """

    __tablename__ = "tourists"

    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    is_lead_tourist: Mapped[bool] = mapped_column(
        default=False, server_default=false(), nullable=False
    )

    full_name_snapshot: Mapped[Str255]
    birth_date_snapshot: Mapped[date | None] = mapped_column(nullable=True)
    passport_series: Mapped[Str32Opt]
    passport_number: Mapped[Str32Opt]
    passport_issued_by: Mapped[Str255Opt]
    passport_issued_date: Mapped[date | None] = mapped_column(nullable=True)
    citizenship_snapshot: Mapped[Str64Opt]
    snapshot_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    deal: Mapped["Deal"] = relationship(back_populates="tourists", lazy="raise")
