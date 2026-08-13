"""Справочник городов."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPkMixin
from app.db.types import Str120

if TYPE_CHECKING:
    from app.reference.countries.models import Country


class City(UUIDPkMixin, TimestampMixin, Base):
    """Город. Глобальный справочник, привязан к стране."""

    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("country_id", "name", name="uq_cities_country_id_name"),)

    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"),
        index=True,
    )
    name: Mapped[Str120]

    country: Mapped["Country"] = relationship(back_populates="cities", lazy="raise")
