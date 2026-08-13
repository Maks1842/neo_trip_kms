"""Зависимости FastAPI для аутентификации и проверки прав."""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.users.models import User

# auto_error=False: собственный обработчик даёт ошибку в общем формате API,
# тогда как встроенный вернул бы тело другого вида.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Пользователь, определённый по токену доступа."""
    if credentials is None:
        raise UnauthorizedError("Требуется авторизация")

    payload = decode_access_token(credentials.credentials)
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Недействительный токен") from exc

    user = await AuthRepository(session).get_user_by_id(user_id)
    if user is None:
        raise UnauthorizedError("Пользователь не найден")
    return user


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Активный пользователь активной компании."""
    if not user.is_active:
        raise ForbiddenError("Учётная запись деактивирована")
    if not user.company.is_active:
        raise ForbiddenError("Доступ компании приостановлен")
    return user


CurrentUser = Annotated[User, Depends(get_current_active_user)]


def require_permission(code: str) -> Callable[..., Coroutine[Any, Any, User]]:
    """Фабрика зависимости, проверяющей наличие права у роли пользователя."""

    async def checker(user: CurrentUser) -> User:
        if not user.role.has_permission(code):
            raise ForbiddenError(f"Требуется право «{code}»")
        return user

    return checker


def client_ip(request: Request) -> str | None:
    """IP клиента с учётом обратного прокси."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
