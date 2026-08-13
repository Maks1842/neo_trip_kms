"""Базовый репозиторий: типовые запросы к одной таблице."""

from collections.abc import Mapping, Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import ColumnElement, CursorResult, UnaryExpression, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class BaseRepository[ModelT: Base]:
    """Доступ к данным одной таблицы.

    Ничего не знает о HTTP, правах и текущем пользователе. Не вызывает commit —
    транзакцией владеет зависимость get_db, иначе одна операция запроса
    перестала бы быть атомарной.
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def get(
        self,
        obj_id: UUID,
        *,
        extra: Sequence[ColumnElement[bool]] = (),
    ) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == obj_id, *extra)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        where: Sequence[ColumnElement[bool]] = (),
        order_by: Sequence[UnaryExpression[Any]] = (),
        limit: int,
        offset: int,
    ) -> Sequence[ModelT]:
        stmt = select(self.model).where(*where).limit(limit).offset(offset)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, *, where: Sequence[ColumnElement[bool]] = ()) -> int:
        stmt = select(func.count()).select_from(self.model).where(*where)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, *, where: Sequence[ColumnElement[bool]]) -> bool:
        stmt = select(select(self.model).where(*where).exists())
        result = await self.session.execute(stmt)
        return bool(result.scalar())

    async def create(self, values: Mapping[str, Any]) -> ModelT:
        obj = self.model(**values)
        self.session.add(obj)
        # flush, а не commit: объект получает идентификатор и попадает в БД,
        # но транзакция остаётся открытой до конца обработки запроса.
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelT, values: Mapping[str, Any]) -> ModelT:
        for field, value in values.items():
            setattr(obj, field, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_where(self, *where: ColumnElement[bool]) -> int:
        result = await self.session.execute(delete(self.model).where(*where))
        await self.session.flush()
        # execute объявлен возвращающим Result, но для DML это всегда CursorResult
        # с доступным числом затронутых строк.
        return cast("CursorResult[Any]", result).rowcount
