"""Первичное наполнение базы: компания, системные роли и администратор.

Запуск:
    uv run python -m scripts.seed

Скрипт идемпотентен — повторный запуск не создаёт дублей.
"""

import asyncio
import logging
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.models import Company
from app.core.config import get_settings
from app.core.security import hash_password

# Реестр импортируется целиком: SQLAlchemy разрешает связи по именам классов,
# и без полного набора моделей маппинг User -> RefreshToken не собирается.
from app.db.registry import metadata as _metadata  # noqa: F401
from app.db.session import async_session_factory, engine
from app.roles.models import Role
from app.users.models import User

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed")

# Системные роли и их права. Состав ролей взят из требований к разграничению
# доступа: администратор, руководитель, менеджер, бухгалтер, маркетолог.
SYSTEM_ROLES: dict[str, list[str]] = {
    "Администратор": ["*"],
    "Руководитель": [
        "reference.read",
        "reference.manage",
        "roles.read",
        "users.read",
        "users.manage",
        "deals.read",
        "deals.manage",
        "clients.read",
        "clients.manage",
        "payments.read",
        "analytics.read",
    ],
    "Менеджер": [
        "reference.read",
        "deals.read",
        "deals.manage",
        "clients.read",
        "clients.manage",
    ],
    "Бухгалтер": [
        "reference.read",
        "deals.read",
        "clients.read",
        "payments.read",
        "payments.manage",
    ],
    "Маркетолог": [
        "reference.read",
        "clients.read",
        "deals.read",
        "analytics.read",
    ],
}


async def seed_company(session: AsyncSession) -> Company:
    settings = get_settings()
    stmt = select(Company).where(Company.slug == settings.first_company_slug)
    company = (await session.execute(stmt)).scalar_one_or_none()
    if company is not None:
        logger.info("Компания «%s» уже существует", company.name)
        return company

    company = Company(
        name=settings.first_company_name,
        slug=settings.first_company_slug,
        white_label_config={},
    )
    session.add(company)
    await session.flush()
    logger.info("Создана компания «%s»", company.name)
    return company


async def seed_roles(session: AsyncSession, company: Company) -> dict[str, Role]:
    result: dict[str, Role] = {}
    for name, permissions in SYSTEM_ROLES.items():
        stmt = select(Role).where(Role.company_id == company.id, Role.name == name)
        role = (await session.execute(stmt)).scalar_one_or_none()
        if role is None:
            role = Role(
                company_id=company.id,
                name=name,
                permissions=permissions,
                is_system=True,
            )
            session.add(role)
            await session.flush()
            logger.info("Создана роль «%s»", name)
        result[name] = role
    return result


async def seed_admin(session: AsyncSession, company: Company, role: Role) -> None:
    settings = get_settings()
    email = settings.first_admin_email.lower()

    stmt = select(User).where(User.email == email)
    if (await session.execute(stmt)).scalar_one_or_none() is not None:
        logger.info("Пользователь %s уже существует", email)
        return

    password = settings.first_admin_password.get_secret_value()
    if not password:
        logger.error("FIRST_ADMIN_PASSWORD не задан в .env — администратор не создан")
        sys.exit(1)
    if password.startswith("change_me"):
        logger.warning(
            "Пароль администратора остался значением по умолчанию. "
            "Смените его сразу после первого входа."
        )

    user = User(
        company_id=company.id,
        role_id=role.id,
        full_name=settings.first_admin_full_name,
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        max_active_deals=0,
    )
    session.add(user)
    await session.flush()
    logger.info("Создан администратор %s", email)


async def main() -> None:
    async with async_session_factory() as session:
        company = await seed_company(session)
        roles = await seed_roles(session, company)
        await seed_admin(session, company, roles["Администратор"])
        await session.commit()
    await engine.dispose()
    logger.info("Наполнение завершено")


if __name__ == "__main__":
    asyncio.run(main())
