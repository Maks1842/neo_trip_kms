"""Роутер ролей."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnElement, or_, select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError, ForbiddenError
from app.roles.models import Role
from app.roles.schemas import RoleCreate, RoleFilter, RoleRead, RoleUpdate
from app.users.models import User


class RoleService(CRUDService[Role, RoleCreate, RoleUpdate]):
    model = Role
    default_order_by = ("name",)
    unique_fields = (("name",),)
    entity_name = "Роль"

    def _tenant_clause(self) -> Sequence[ColumnElement[bool]]:
        # Роли компании и системные роли (company_id IS NULL) видны вместе:
        # системные нужны для назначения пользователям.
        return [
            or_(
                Role.company_id == self.actor.company_id,
                Role.company_id.is_(None),
            )
        ]

    async def _prepare_update(self, obj: Role, values: dict[str, Any]) -> dict[str, Any]:
        if obj.is_system:
            raise ForbiddenError("Системную роль нельзя изменять")
        return values

    async def _check_delete(self, obj: Role) -> None:
        if obj.is_system:
            raise ForbiddenError("Системную роль нельзя удалить")
        stmt = select(User.id).where(User.role_id == obj.id).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Роль назначена пользователям и не может быть удалена")


router = build_crud_router(
    service_class=RoleService,
    prefix="/roles",
    tags=["Роли"],
    read_schema=RoleRead,
    create_schema=RoleCreate,
    update_schema=RoleUpdate,
    filter_schema=RoleFilter,
    permissions=CrudPermissions(read="roles.read", write="roles.manage"),
    resource_name="roles",
)
