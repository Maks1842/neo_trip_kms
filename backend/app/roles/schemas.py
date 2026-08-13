"""Схемы ролей."""

from collections.abc import Sequence
from typing import Final

from pydantic import Field, field_validator
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.roles.models import Role

# Полный список прав, которые понимает система. Проверка по нему не даёт завести
# роль с опечаткой в коде права — такая роль молча не работала бы.
AVAILABLE_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        "*",
        "reference.read",
        "reference.manage",
        "roles.read",
        "roles.manage",
        "users.read",
        "users.manage",
        "deals.read",
        "deals.manage",
        "clients.read",
        "clients.manage",
        "payments.read",
        "payments.manage",
        "analytics.read",
    }
)


def _validate_permissions(codes: list[str]) -> list[str]:
    unknown = sorted(set(codes) - AVAILABLE_PERMISSIONS)
    if unknown:
        raise ValueError(f"Неизвестные права: {', '.join(unknown)}")
    return codes


class RoleCreate(BaseSchema):
    name: str = Field(max_length=120)
    permissions: list[str] = Field(default_factory=list)

    @field_validator("permissions")
    @classmethod
    def check_permissions(cls, value: list[str]) -> list[str]:
        return _validate_permissions(value)


class RoleUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=120)
    permissions: list[str] | None = None

    @field_validator("permissions")
    @classmethod
    def check_permissions(cls, value: list[str] | None) -> list[str] | None:
        return _validate_permissions(value) if value is not None else value


class RoleRead(IdSchema, TimestampSchema):
    name: str
    permissions: list[str]
    is_system: bool


class RoleFilter(BaseFilter):
    search: str | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        if not self.search:
            return []
        return [Role.name.ilike(f"%{self.search}%")]
