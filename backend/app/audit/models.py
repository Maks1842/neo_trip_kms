"""Модель журнала аудита."""

from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import AuditAction, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import IPAddressOpt, JSONBDict, Str64


class AuditLog(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Запись журнала изменений.

    Единая полиморфная таблица вместо history-таблицы на каждую модель: иначе
    сквозной ответ на вопрос «кто и что менял за последний час» требовал бы
    объединения двух десятков таблиц.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    entity_type: Mapped[Str64]
    entity_id: Mapped[UUID]
    # NULL означает системное действие: импорт, работа планировщика, обработка вебхука.
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[AuditAction] = mapped_column(pg_enum(AuditAction, "audit_action"))
    # Различия полей до и после изменения.
    field_changes: Mapped[JSONBDict]
    ip_address: Mapped[IPAddressOpt]
