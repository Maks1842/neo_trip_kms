"""Модель платежа."""

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import PaymentDirection, PaymentMethod, PaymentStatus, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import Money, Str255Opt, TimestampOpt


class Payment(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Факт движения денег по сделке.

    Отдельной модели счёта нет: печатный счёт — это документ, а сумма к оплате
    берётся из сделки и её позиций. Здесь фиксируется только реальное движение денег,
    приходящее из эквайринга или из учётной системы.
    """

    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount_minor > 0", name="amount_positive"),)

    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id", ondelete="RESTRICT"), index=True)
    direction: Mapped[PaymentDirection] = mapped_column(
        pg_enum(PaymentDirection, "payment_direction")
    )
    amount_minor: Mapped[Money]
    currency_id: Mapped[UUID] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"))
    status: Mapped[PaymentStatus] = mapped_column(
        pg_enum(PaymentStatus, "payment_status"), default=PaymentStatus.PENDING, index=True
    )
    method: Mapped[PaymentMethod] = mapped_column(pg_enum(PaymentMethod, "payment_method"))
    # Идентификатор транзакции во внешней системе — ключ сверки с банком,
    # эквайрингом или учётной системой.
    external_transaction_id: Mapped[Str255Opt] = mapped_column(index=True)
    paid_at: Mapped[TimestampOpt]
