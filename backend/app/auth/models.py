"""Модель refresh-токена."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPkMixin
from app.db.types import IPAddressOpt, Str255Opt, TimestampOpt

if TYPE_CHECKING:
    from app.users.models import User


class RefreshToken(UUIDPkMixin, TimestampMixin, Base):
    """Выданный refresh-токен.

    Токены хранятся в базе, а не только у клиента, чтобы работали выход из системы
    и мгновенный отзыв доступа уволенному сотруднику. Без этого токен жил бы до
    истечения срока, что для системы с персональными данными клиентов неприемлемо.

    В базе лежит sha256-хеш токена: утечка дампа не даёт возможности им воспользоваться.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    revoked_at: Mapped[TimestampOpt]

    # Ссылка на токен, выданный взамен текущего при ротации. Позволяет обнаружить
    # повторное использование старого токена и отозвать всю цепочку.
    replaced_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )

    user_agent: Mapped[Str255Opt]
    ip_address: Mapped[IPAddressOpt]

    user: Mapped["User"] = relationship(back_populates="refresh_tokens", lazy="raise")

    @property
    def is_active(self) -> bool:
        """Токен пригоден к использованию."""
        from datetime import UTC

        return self.revoked_at is None and self.expires_at > datetime.now(UTC)
