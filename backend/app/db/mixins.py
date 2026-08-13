"""Миксины моделей: первичный ключ, аудит-поля, мультитенантность, флаг активности."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, func, true
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.common.ids import uuid7


class UUIDPkMixin:
    """Первичный ключ UUIDv7, генерируемый на стороне приложения.

    Генерация в Python, а не в БД, нужна для offline-first клиента: он должен уметь
    создать запись и знать её идентификатор до синхронизации с сервером.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    """Аудит-поля создания и изменения записи.

    Применяется ко всем таблицам без исключения — в исходной схеме эти поля были
    расставлены выборочно, что делало невозможной сортировку и отладку по времени.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CompanyMixin:
    """Привязка записи к компании-арендатору.

    company_id денормализован во все таблицы (кроме глобальных справочников), чтобы
    фильтрация по тенанту не требовала JOIN к родителю и чтобы позже можно было
    включить PostgreSQL RLS.
    """

    @declared_attr
    def company_id(cls) -> Mapped[UUID]:  # noqa: N805
        return mapped_column(
            ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )


class ActiveMixin:
    """Флаг активности.

    Полноценного soft delete в проекте нет: записи, которые нельзя удалять
    (сотрудники, объекты размещения, партнёры), деактивируются этим флагом.
    """

    is_active: Mapped[bool] = mapped_column(default=True, server_default=true(), nullable=False)
