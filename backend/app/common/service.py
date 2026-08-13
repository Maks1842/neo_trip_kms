"""Базовый CRUD-сервис."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ColumnElement, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.filters import BaseFilter
from app.common.pagination import PageParams
from app.common.repository import BaseRepository
from app.core.exceptions import ConflictError, NotFoundError
from app.db.base import Base

if TYPE_CHECKING:
    from app.users.models import User


class CRUDService[ModelT: Base, CreateT: BaseModel, UpdateT: BaseModel]:
    """Типовые операции над сущностью с учётом прав и принадлежности компании.

    Изоляция тенантов реализована здесь и только здесь: ни один конкретный сервис
    не пишет условие по company_id руками. Забытый фильтр — самый вероятный способ
    показать одной компании данные другой, поэтому он вынесен в общий код,
    а не оставлен на дисциплину.
    """

    model: ClassVar[type[Any]]

    # False для глобальных справочников: стран, городов, валют.
    tenant_scoped: ClassVar[bool] = True
    default_order_by: ClassVar[tuple[str, ...]] = ("created_at",)
    # Наборы полей, уникальность которых проверяется до вставки, чтобы вернуть
    # понятный 409, а не ошибку драйвера.
    unique_fields: ClassVar[tuple[tuple[str, ...], ...]] = ()
    entity_name: ClassVar[str] = "Запись"

    def __init__(self, session: AsyncSession, actor: "User") -> None:
        self.session = session
        self.actor = actor
        self.repository: BaseRepository[Any] = BaseRepository(session, self.model)

    # ---------- Внутренние помощники ----------

    def _tenant_clause(self) -> Sequence[ColumnElement[bool]]:
        if not self.tenant_scoped:
            return []
        return [self.model.company_id == self.actor.company_id]

    def _order_clause(self, page: PageParams) -> Sequence[UnaryExpression[Any]]:
        field_name = page.order_by or self.default_order_by[0]
        column = getattr(self.model, field_name, None)
        if column is None:
            # Неизвестное поле сортировки не должно ронять запрос: откатываемся
            # к сортировке по умолчанию.
            column = getattr(self.model, self.default_order_by[0])
        return [column.desc() if page.desc else column.asc()]

    async def _ensure_unique(
        self,
        values: dict[str, Any],
        *,
        exclude_id: UUID | None = None,
    ) -> None:
        for field_group in self.unique_fields:
            if not all(field in values for field in field_group):
                continue
            conditions: list[ColumnElement[bool]] = [
                getattr(self.model, field) == values[field] for field in field_group
            ]
            conditions.extend(self._tenant_clause())
            if exclude_id is not None:
                conditions.append(self.model.id != exclude_id)
            if await self.repository.exists(where=conditions):
                fields = ", ".join(field_group)
                raise ConflictError(
                    f"{self.entity_name} с такими значениями полей ({fields}) уже существует"
                )

    # ---------- Точки расширения ----------

    async def _prepare_create(self, values: dict[str, Any]) -> dict[str, Any]:
        """Дополнительная подготовка и валидация перед созданием."""
        return values

    async def _prepare_update(self, obj: ModelT, values: dict[str, Any]) -> dict[str, Any]:
        """Дополнительная подготовка и валидация перед обновлением."""
        return values

    async def _check_delete(self, obj: ModelT) -> None:
        """Проверка допустимости удаления."""
        return None

    # ---------- Операции ----------

    async def get(self, obj_id: UUID) -> ModelT:
        obj = await self.repository.get(obj_id, extra=self._tenant_clause())
        if obj is None:
            # Для записи чужой компании возвращается именно 404, а не 403:
            # иначе по коду ответа можно было бы установить факт её существования.
            raise NotFoundError(f"{self.entity_name} не найдена")
        return cast("ModelT", obj)

    async def list(
        self,
        page: PageParams,
        filters: BaseFilter | None = None,
    ) -> tuple[Sequence[ModelT], int]:
        conditions: list[ColumnElement[bool]] = list(self._tenant_clause())
        if filters is not None:
            conditions.extend(filters.conditions())
        items = cast(
            "Sequence[ModelT]",
            await self.repository.list(
                where=conditions,
                order_by=self._order_clause(page),
                limit=page.limit,
                offset=page.offset,
            ),
        )
        total = await self.repository.count(where=conditions)
        return items, total

    async def create(self, data: CreateT) -> ModelT:
        values = data.model_dump(exclude_unset=True)
        if self.tenant_scoped:
            values["company_id"] = self.actor.company_id
        values = await self._prepare_create(values)
        await self._ensure_unique(values)
        return cast("ModelT", await self.repository.create(values))

    async def update(self, obj_id: UUID, data: UpdateT) -> ModelT:
        obj = await self.get(obj_id)
        values = data.model_dump(exclude_unset=True)
        if not values:
            return obj
        values = await self._prepare_update(obj, values)
        await self._ensure_unique(values, exclude_id=obj_id)
        return cast("ModelT", await self.repository.update(obj, values))

    async def delete(self, obj_id: UUID) -> None:
        obj = await self.get(obj_id)
        await self._check_delete(obj)
        await self.repository.delete(obj)
