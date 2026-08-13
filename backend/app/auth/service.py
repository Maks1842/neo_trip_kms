"""Бизнес-логика авторизации."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import TokenPair
from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expires_at,
    verify_password,
)
from app.users.models import User


class AuthService:
    """Вход, обновление и отзыв токенов."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AuthRepository(session)
        self.settings = get_settings()

    async def login(
        self,
        email: str,
        password: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        user = await self.repository.get_user_by_email(email)

        # Одинаковая ошибка для несуществующего пользователя и неверного пароля:
        # иначе по ответу можно перебором составить список учётных записей.
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")

        self._ensure_user_can_login(user)
        await self.repository.touch_last_login(user)
        return await self._issue_pair(user, user_agent=user_agent, ip_address=ip_address)

    async def refresh(
        self,
        refresh_token: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.repository.get_token_by_hash(token_hash)
        if stored is None:
            raise UnauthorizedError("Недействительный refresh-токен")

        if stored.revoked_at is not None:
            # Токен уже использовался. Это либо кража, либо повтор запроса —
            # в обоих случаях безопаснее отозвать всю цепочку и потребовать
            # повторного входа.
            await self.repository.revoke_all_for_user(stored.user_id)
            # Коммит здесь обязателен и сделан в обход общего правила «транзакцией
            # владеет get_db»: следом поднимается исключение, а оно приводит к
            # откату — и отзыв скомпрометированных токенов был бы потерян.
            await self.session.commit()
            raise UnauthorizedError("Refresh-токен отозван, требуется повторный вход")

        if stored.expires_at <= datetime.now(UTC):
            raise UnauthorizedError("Срок действия refresh-токена истёк")

        user = await self.repository.get_user_by_id(stored.user_id)
        if user is None:
            raise UnauthorizedError("Пользователь не найден")
        self._ensure_user_can_login(user)

        pair = await self._issue_pair(user, user_agent=user_agent, ip_address=ip_address)
        new_token = await self.repository.get_token_by_hash(hash_refresh_token(pair.refresh_token))
        await self.repository.revoke(stored, replaced_by_id=new_token.id if new_token else None)
        return pair

    async def logout(self, refresh_token: str) -> None:
        stored = await self.repository.get_token_by_hash(hash_refresh_token(refresh_token))
        # Молча игнорируем неизвестный токен: выход должен быть идемпотентным.
        if stored is not None and stored.revoked_at is None:
            await self.repository.revoke(stored)

    async def logout_all(self, user: User) -> int:
        return await self.repository.revoke_all_for_user(user.id)

    async def change_password(self, user: User, current: str, new: str) -> None:
        if not verify_password(current, user.password_hash):
            raise UnauthorizedError("Текущий пароль указан неверно")
        user.password_hash = hash_password(new)
        user.password_changed_at = datetime.now(UTC)
        await self.session.flush()
        # После смены пароля все выданные сессии должны прекратиться.
        await self.repository.revoke_all_for_user(user.id)

    # ---------- Внутреннее ----------

    def _ensure_user_can_login(self, user: User) -> None:
        if not user.is_active:
            raise ForbiddenError("Учётная запись деактивирована")
        if not user.company.is_active:
            raise ForbiddenError("Доступ компании приостановлен")

    async def _issue_pair(
        self,
        user: User,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> TokenPair:
        access = create_access_token(user.id, user.company_id)
        raw_refresh, refresh_hash = generate_refresh_token()
        await self.repository.create_token(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=refresh_token_expires_at(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return TokenPair(
            access_token=access,
            refresh_token=raw_refresh,
            expires_in=self.settings.access_token_expire_minutes * 60,
        )
