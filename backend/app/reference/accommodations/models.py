"""Объекты размещения, программы и внутренние заметки."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import AccommodationNoteSource, AccommodationType, pg_enum
from app.db.mixins import ActiveMixin, CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import LongText, LongTextOpt, PercentOptional, Str120, Str255, Str255Opt

if TYPE_CHECKING:
    from app.reference.tariff_entries.models import TariffEntry


class Accommodation(UUIDPkMixin, TimestampMixin, CompanyMixin, ActiveMixin, Base):
    """Отель или санаторий.

    Это справочник и прайс, а не inventory: остатков номеров, стоп-сейлов и календаря
    доступности здесь нет — они относятся к PMS, который в текущий трек не входит.
    """

    __tablename__ = "accommodations"

    name: Mapped[Str255]
    type: Mapped[AccommodationType] = mapped_column(
        pg_enum(AccommodationType, "accommodation_type")
    )
    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"), index=True
    )
    city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), index=True)
    address: Mapped[Str255Opt]
    description: Mapped[LongTextOpt]
    rating: Mapped[PercentOptional]

    programs: Mapped[list["AccommodationProgram"]] = relationship(
        back_populates="accommodation",
        lazy="raise",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["AccommodationNote"]] = relationship(
        back_populates="accommodation",
        lazy="raise",
        cascade="all, delete-orphan",
    )


class AccommodationProgram(UUIDPkMixin, TimestampMixin, CompanyMixin, ActiveMixin, Base):
    """Программа проживания или тип номера внутри объекта размещения."""

    __tablename__ = "accommodation_programs"
    __table_args__ = (CheckConstraint("capacity > 0", name="capacity_positive"),)

    accommodation_id: Mapped[UUID] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[Str255]
    capacity: Mapped[int] = mapped_column(default=1, server_default="1", nullable=False)
    description: Mapped[LongTextOpt]

    accommodation: Mapped["Accommodation"] = relationship(back_populates="programs", lazy="raise")
    tariff_entries: Mapped[list["TariffEntry"]] = relationship(
        back_populates="program",
        lazy="raise",
        cascade="all, delete-orphan",
    )


class AccommodationNote(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Внутренняя заметка менеджера об объекте размещения.

    Накопление такого опыта — основа будущей базы знаний по объектам.
    """

    __tablename__ = "accommodation_notes"

    accommodation_id: Mapped[UUID] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"),
        index=True,
    )
    author_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    text: Mapped[LongText]
    source: Mapped[AccommodationNoteSource] = mapped_column(
        pg_enum(AccommodationNoteSource, "accommodation_note_source"),
        default=AccommodationNoteSource.MANUAL,
    )
    title: Mapped[Str120] = mapped_column(default="")

    accommodation: Mapped["Accommodation"] = relationship(back_populates="notes", lazy="raise")
