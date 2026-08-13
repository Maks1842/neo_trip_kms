"""Справочник стран."""

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPkMixin
from app.db.types import Str2, Str120

if TYPE_CHECKING:
    from app.reference.cities.models import City


class Country(UUIDPkMixin, TimestampMixin, Base):
    """Страна.

    Глобальный справочник: общий для всех компаний, поэтому company_id отсутствует.
    """

    __tablename__ = "countries"

    name: Mapped[Str120] = mapped_column(unique=True)
    code: Mapped[Str2] = mapped_column(unique=True)  # ISO 3166-1 alpha-2

    cities: Mapped[list["City"]] = relationship(back_populates="country", lazy="raise")
