"""Доступ к данным refresh-токенов и пользователей при авторизации."""

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import CursorResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import RefreshToken
from app.users.models import User


class AuthRepository:
    """Запросы, необходимые для входа и работы с токенами."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email.lower())
            .options(selectinload(User.role), selectinload(User.company))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.role), selectinload(User.company))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_token(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def revoke(self, token: RefreshToken, *, replaced_by_id: UUID | None = None) -> None:
        token.revoked_at = datetime.now(UTC)
        token.replaced_by_id = replaced_by_id
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Отзывает все активные токены пользователя.

        Используется при выходе со всех устройств, смене пароля и при обнаружении
        повторного использования уже отозванного токена.
        """
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return cast("CursorResult[Any]", result).rowcount

    async def touch_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(UTC)
        await self.session.flush()
