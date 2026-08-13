"""Базовые Pydantic-схемы, общие для всех доменов."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема: читает данные из атрибутов ORM-объектов."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class IdSchema(BaseSchema):
    """Схема ответа с идентификатором."""

    id: UUID


class TimestampSchema(BaseSchema):
    """Аудит-поля в ответе."""

    created_at: datetime
    updated_at: datetime


class Page[ItemT](BaseSchema):
    """Страница списка."""

    items: list[ItemT]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseSchema):
    field: str | None = None
    message: str
    type: str | None = None


class ErrorPayload(BaseSchema):
    code: str
    message: str
    details: list[dict[str, Any]] = []
    request_id: str | None = None


class ErrorResponse(BaseSchema):
    """Единый формат тела ошибки — используется только для документации OpenAPI."""

    error: ErrorPayload
