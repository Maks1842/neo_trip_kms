"""Справочник валют."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin, UUIDPkMixin
from app.db.types import Str3, Str16, Str64


class Currency(UUIDPkMixin, TimestampMixin, ActiveMixin, Base):
    """Валюта по стандарту ISO 4217.

    В исходной схеме валюта была свободной строкой в четырёх таблицах. Справочник
    позволяет добавить валюту без миграции и хранит minor_unit — число знаков после
    запятой, без которого невозможно пересчитать сумму из копеек в рубли.
    """

    __tablename__ = "currencies"
    __table_args__ = (
        CheckConstraint("minor_unit >= 0 AND minor_unit <= 4", name="minor_unit_range"),
    )

    code: Mapped[Str3] = mapped_column(unique=True)  # ISO 4217 alpha-3: RUB, USD, EUR
    name: Mapped[Str64]
    symbol: Mapped[Str16]
    # Число знаков после запятой: 2 для рубля и доллара, 0 для иены.
    minor_unit: Mapped[int] = mapped_column(default=2, server_default="2", nullable=False)
