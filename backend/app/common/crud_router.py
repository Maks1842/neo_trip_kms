"""Фабрика REST-роутеров для однотипных CRUD-ресурсов.

Десять справочников с одинаковым набором операций, написанные вручную, — это около
полутора тысяч строк дублирования и десять мест, где можно забыть проверку прав
или фильтр по компании. Фабрика превращает подключение справочника в объявление
схем и одного вызова.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.common.filters import BaseFilter
from app.common.pagination import PageDep
from app.common.schemas import Page
from app.common.service import CRUDService
from app.db.session import get_db
from app.users.models import User


@dataclass(frozen=True, slots=True)
class CrudPermissions:
    """Коды прав, необходимых для операций ресурса."""

    read: str
    write: str
    delete: str | None = None

    @property
    def delete_code(self) -> str:
        return self.delete or self.write


def build_crud_router(
    *,
    service_class: type[CRUDService[Any, Any, Any]],
    prefix: str,
    tags: list[str | Enum],
    read_schema: type[BaseModel],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    permissions: CrudPermissions,
    filter_schema: type[BaseFilter] | None = None,
    resource_name: str | None = None,
) -> APIRouter:
    """Собирает роутер с пятью типовыми операциями."""
    router = APIRouter(prefix=prefix, tags=tags)
    name = resource_name or prefix.strip("/").replace("-", "_")

    DbDep = Annotated[AsyncSession, Depends(get_db)]  # noqa: N806 — это алиас типа

    # Если ресурс не объявил своих фильтров, используется базовый: он не добавляет
    # условий, но позволяет не разветвлять сигнатуры обработчиков.
    effective_filter = filter_schema or BaseFilter
    FiltersDep = Annotated[  # noqa: N806 — это алиас типа
        effective_filter,  # type: ignore[valid-type]
        Depends(effective_filter),
    ]

    @router.get(
        "/",
        response_model=Page[read_schema],  # type: ignore[valid-type]
        operation_id=f"{name}_list",
        summary="Список записей",
    )
    async def list_items(
        session: DbDep,
        page: PageDep,
        filters: FiltersDep,
        user: Annotated[User, Depends(require_permission(permissions.read))],
    ) -> Any:
        service = service_class(session, user)
        items, total = await service.list(page, filters)
        return Page[read_schema](  # type: ignore[valid-type]
            items=[read_schema.model_validate(item) for item in items],
            total=total,
            limit=page.limit,
            offset=page.offset,
        )

    @router.post(
        "/",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        operation_id=f"{name}_create",
        summary="Создание записи",
    )
    async def create_item(
        session: DbDep,
        data: create_schema,  # type: ignore[valid-type]
        user: Annotated[User, Depends(require_permission(permissions.write))],
    ) -> Any:
        service = service_class(session, user)
        return await service.create(data)

    @router.get(
        "/{item_id}",
        response_model=read_schema,
        operation_id=f"{name}_get",
        summary="Чтение записи",
    )
    async def get_item(
        item_id: UUID,
        session: DbDep,
        user: Annotated[User, Depends(require_permission(permissions.read))],
    ) -> Any:
        service = service_class(session, user)
        return await service.get(item_id)

    @router.patch(
        "/{item_id}",
        response_model=read_schema,
        operation_id=f"{name}_update",
        summary="Изменение записи",
    )
    async def update_item(
        item_id: UUID,
        data: update_schema,  # type: ignore[valid-type]
        session: DbDep,
        user: Annotated[User, Depends(require_permission(permissions.write))],
    ) -> Any:
        service = service_class(session, user)
        return await service.update(item_id, data)

    @router.delete(
        "/{item_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        operation_id=f"{name}_delete",
        summary="Удаление записи",
    )
    async def delete_item(
        item_id: UUID,
        session: DbDep,
        user: Annotated[User, Depends(require_permission(permissions.delete_code))],
    ) -> None:
        service = service_class(session, user)
        await service.delete(item_id)

    return router
