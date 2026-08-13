"""Базовый класс ORM-моделей."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID

from sqlalchemy import Date, MetaData, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped

# Соглашение об именовании ограничений. Должно быть задано ДО первой миграции:
# иначе имена придумает PostgreSQL, и каждая последующая автогенерация Alembic
# будет предлагать переименования.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Общий базовый класс всех моделей."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Сквозное соответствие Python-типов и типов колонок: задаётся один раз,
    # чтобы не повторять Numeric/JSONB/TIMESTAMP в каждой модели.
    # Это конфигурация SQLAlchemy, а не изменяемое состояние экземпляра.
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        str: String(255),
        datetime: TIMESTAMP(timezone=True),
        date: Date,
        Decimal: Numeric(12, 2),
        dict[str, Any]: JSONB,
    }

    if TYPE_CHECKING:
        # Первичный ключ объявляет миксин UUIDPkMixin, но общий код (репозиторий)
        # обращается к нему через базовый тип. Аннотация видна только проверяющему
        # типы: во время выполнения SQLAlchemy колонку отсюда не создаёт.
        id: Mapped[UUID]

    def __repr__(self) -> str:
        pk = getattr(self, "id", None)
        return f"<{type(self).__name__} id={pk}>"
