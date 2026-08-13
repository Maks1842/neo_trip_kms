"""Доменные исключения приложения.

Сервисный слой ничего не знает про HTTP и никогда не поднимает HTTPException —
он поднимает эти исключения, а перевод в HTTP-ответ делают обработчики в handlers.py.
"""

from typing import Any


class AppError(Exception):
    """Базовое исключение приложения."""

    code: str = "error"
    status_code: int = 500
    default_message: str = "Внутренняя ошибка приложения"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or []
        super().__init__(self.message)


class NotFoundError(AppError):
    """Запрашиваемый объект не найден или недоступен текущему пользователю."""

    code = "not_found"
    status_code = 404
    default_message = "Объект не найден"


class ConflictError(AppError):
    """Конфликт состояния: нарушение уникальности, попытка удалить используемую запись."""

    code = "conflict"
    status_code = 409
    default_message = "Операция конфликтует с текущим состоянием данных"


class BusinessValidationError(AppError):
    """Нарушение бизнес-правила, которое нельзя выразить схемой Pydantic."""

    code = "validation_error"
    status_code = 422
    default_message = "Данные не прошли проверку"


class UnauthorizedError(AppError):
    """Отсутствует или недействителен токен доступа."""

    code = "unauthorized"
    status_code = 401
    default_message = "Требуется авторизация"


class ForbiddenError(AppError):
    """Пользователь аутентифицирован, но не имеет права на операцию."""

    code = "forbidden"
    status_code = 403
    default_message = "Недостаточно прав для выполнения операции"
