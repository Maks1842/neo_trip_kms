"""Модель роли (RBAC)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, false
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPkMixin
from app.db.types import Str120

if TYPE_CHECKING:
    from app.users.models import User


class Role(UUIDPkMixin, TimestampMixin, Base):
    """Роль сотрудника с набором прав.

    Права хранятся плоским списком строковых кодов вида "reference.manage".
    Отдельная таблица прав появится, если понадобится гранулярность на уровне записей.
    """

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_roles_company_id_name"),)

    # NULL означает системную роль, общую для всех компаний.
    company_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[Str120]
    permissions: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")
    # Системные роли создаются скриптом наполнения и не редактируются через API.
    is_system: Mapped[bool] = mapped_column(default=False, server_default=false(), nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role", lazy="raise")

    def has_permission(self, code: str) -> bool:
        """Проверка права. Код "*" означает полный доступ."""
        return "*" in self.permissions or code in self.permissions
