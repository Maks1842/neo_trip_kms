"""Пароли и JWT."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

# argon2id — текущая рекомендация OWASP для хранения паролей.
_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hasher.verify(password, password_hash)


def create_access_token(user_id: UUID, company_id: UUID) -> str:
    """Короткоживущий токен доступа.

    company_id кладётся в полезную нагрузку, чтобы не запрашивать его из БД
    на каждом обращении к API.
    """
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "company_id": str(company_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Проверка подписи и срока действия токена доступа."""
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Срок действия токена истёк") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Недействительный токен") from exc

    if payload.get("type") != "access":
        # Refresh-токен не должен приниматься как токен доступа.
        raise UnauthorizedError("Недействительный тип токена")
    return payload


def generate_refresh_token() -> tuple[str, str]:
    """Создаёт refresh-токен и его хеш.

    Клиенту уходит сам токен, в базу сохраняется только хеш: утечка дампа базы
    не позволит воспользоваться чужой сессией.
    """
    token = secrets.token_urlsafe(48)
    return token, hash_refresh_token(token)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_token_expires_at() -> datetime:
    settings = get_settings()
    return datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
