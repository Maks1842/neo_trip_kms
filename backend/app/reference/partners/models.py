"""Справочник партнёров и субагентов."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import PartnerType, pg_enum
from app.db.mixins import ActiveMixin, CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import PercentOptional, Str32Opt, Str255, Str255Opt


class Partner(UUIDPkMixin, TimestampMixin, CompanyMixin, ActiveMixin, Base):
    """Внешний субагент, реферер или партнёр, приводящий сделки за комиссию.

    Модель намеренно минимальная: хранится только процент комиссии, история начислений
    не ведётся. Полноценный леджер — отдельная задача, связанная с финансовым контуром.
    """

    __tablename__ = "partners"
    __table_args__ = (
        CheckConstraint(
            "commission_percent IS NULL OR (commission_percent >= 0 AND commission_percent <= 100)",
            name="commission_percent_range",
        ),
    )

    name: Mapped[Str255]
    type: Mapped[PartnerType] = mapped_column(pg_enum(PartnerType, "partner_type"))
    contact_phone: Mapped[Str32Opt]
    contact_email: Mapped[Str255Opt]
    commission_percent: Mapped[PercentOptional]
