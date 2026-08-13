"""Тарифная сетка объектов размещения."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.money import to_major
from app.db.base import Base
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import JSONBDict, Money
from app.reference.currencies.models import Currency

if TYPE_CHECKING:
    from app.reference.accommodations.models import AccommodationProgram


class TariffEntry(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Цена программы размещения на сезон — источник данных для калькулятора стоимости."""

    __tablename__ = "tariff_entries"
    __table_args__ = (
        CheckConstraint("season_start <= season_end", name="season_order"),
        CheckConstraint("price_minor >= 0", name="price_non_negative"),
    )

    accommodation_id: Mapped[UUID] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"),
        index=True,
    )
    program_id: Mapped[UUID] = mapped_column(
        ForeignKey("accommodation_programs.id", ondelete="CASCADE"),
        index=True,
    )
    season_start: Mapped[date]
    season_end: Mapped[date]
    # Состав туристов и наценки за него: структура меняется от объекта к объекту,
    # поэтому хранится документом, а не отдельными колонками.
    occupancy_config: Mapped[JSONBDict]
    price_minor: Mapped[Money]
    currency_id: Mapped[UUID] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        index=True,
    )

    program: Mapped["AccommodationProgram"] = relationship(
        back_populates="tariff_entries", lazy="raise"
    )
    # Валюта загружается всегда: без её minor_unit невозможно показать цену
    # в основных единицах, а справочник тарифов читается только вместе с ценой.
    currency: Mapped["Currency"] = relationship(lazy="selectin")

    @property
    def price(self) -> Decimal:
        """Цена в основных единицах валюты — представление для API."""
        return to_major(self.price_minor, self.currency.minor_unit)

    @property
    def currency_code(self) -> str:
        return self.currency.code
