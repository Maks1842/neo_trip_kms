"""Модель задачи."""

from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import TaskCreatedBy, TaskStatus, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import LongTextOpt, Str255, TimestampOpt


class Task(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Задача менеджера — ручная или поставленная автоматически при смене этапа сделки."""

    __tablename__ = "tasks"

    deal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True
    )
    assignee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[Str255]
    description: Mapped[LongTextOpt]
    due_at: Mapped[TimestampOpt]
    status: Mapped[TaskStatus] = mapped_column(
        pg_enum(TaskStatus, "task_status"), default=TaskStatus.OPEN, index=True
    )
    created_by: Mapped[TaskCreatedBy] = mapped_column(
        pg_enum(TaskCreatedBy, "task_created_by"), default=TaskCreatedBy.MANUAL
    )
    completed_at: Mapped[TimestampOpt]
