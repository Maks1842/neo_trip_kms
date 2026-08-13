"""Модель пользователя CRM."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import Str32Opt, Str255, TimestampOpt

if TYPE_CHECKING:
    from app.auth.models import RefreshToken
    from app.companies.models import Company
    from app.roles.models import Role


class User(UUIDPkMixin, TimestampMixin, CompanyMixin, ActiveMixin, Base):
    """Сотрудник компании — пользователь CRM.

    Уволенных деактивируем через is_active, а не удаляем: на пользователя ссылаются
    сделки, задачи и записи аудита.
    """

    __tablename__ = "users"

    full_name: Mapped[Str255]
    email: Mapped[Str255] = mapped_column(unique=True, index=True)
    phone: Mapped[Str32Opt]
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), index=True)

    # Индивидуальный лимит сделок «в работе» — основа механики авто-возврата
    # заявки в общий сток при перегрузке менеджера.
    max_active_deals: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)

    # Учётные данные. В исходной схеме этих полей не было — без них авторизация
    # не собирается.
    password_hash: Mapped[Str255]
    last_login_at: Mapped[TimestampOpt]
    password_changed_at: Mapped[TimestampOpt]

    company: Mapped["Company"] = relationship(back_populates="users", lazy="raise")
    role: Mapped["Role"] = relationship(back_populates="users", lazy="raise")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        lazy="raise",
        cascade="all, delete-orphan",
    )
