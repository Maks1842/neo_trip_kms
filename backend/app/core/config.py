"""Конфигурация приложения.

Все настройки читаются из переменных окружения или файла .env в корне репозитория.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень репозитория: файл лежит в backend/app/core/, поэтому поднимаемся на три уровня.
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", Path(".env")),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---------- Приложение ----------
    app_name: str = "Neo Trip CRM"
    app_version: str = "0.1.0"
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # ---------- PostgreSQL ----------
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "neo_trip"
    postgres_user: str = "neo_trip"
    postgres_password: SecretStr = SecretStr("")
    # Вывод SQL-запросов вынесен из DEBUG в отдельный флаг: он нужен точечно при
    # разборе конкретного запроса, а не всё время, пока включена отладка.
    db_echo: bool = False

    # ---------- JWT ----------
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # ---------- Пагинация ----------
    default_page_size: int = 50
    max_page_size: int = 200

    # ---------- Первичное наполнение (scripts/seed.py) ----------
    first_company_name: str = "Демо агентство"
    first_company_slug: str = "demo"
    first_admin_email: str = "admin@neotrip.local"
    first_admin_password: SecretStr = SecretStr("")
    first_admin_full_name: str = "Администратор системы"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """DSN для асинхронного подключения приложения к БД."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Настройки читаются один раз за время жизни процесса."""
    return Settings()
