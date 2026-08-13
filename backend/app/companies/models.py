"""Модель компании-арендатора."""

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin, UUIDPkMixin
from app.db.types import JSONBDict, Str64, Str255

if TYPE_CHECKING:
    from app.users.models import User


class Company(UUIDPkMixin, TimestampMixin, ActiveMixin, Base):
    """Компания-арендатор (агентство) — владелец всех данных в рамках мультитенантности.

    Заложена с первого дня, даже пока тенант один: добавить мультитенантность позже
    без миграции данных с нуля практически невозможно.
    """

    __tablename__ = "companies"

    name: Mapped[Str255]
    slug: Mapped[Str64] = mapped_column(unique=True)
    white_label_config: Mapped[JSONBDict]

    users: Mapped[list["User"]] = relationship(
        back_populates="company",
        lazy="raise",
    )
