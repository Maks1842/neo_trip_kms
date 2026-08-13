"""Точка входа приложения."""

import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers

# Импорт реестра регистрирует ВСЕ модели: связи между ними задаются строковыми
# именами классов и разрешаются только после того, как каждый класс объявлен.
# Импортируется metadata, а не пакет: имя app конфликтовало бы с переменной
# приложения в конце модуля.
from app.db.registry import metadata as _metadata  # noqa: F401
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Проверка доступности БД при старте и освобождение пула при остановке."""
    settings = get_settings()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Подключение к базе данных установлено")
    except Exception:
        # Приложение продолжает запуск: контейнер БД может подниматься дольше,
        # а эндпоинт /health/db покажет реальное состояние.
        logger.exception("Не удалось подключиться к базе данных при старте")

    logger.info("%s запущен в окружении %s", settings.app_name, settings.app_env)
    yield
    await engine.dispose()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Присваивает каждому запросу идентификатор для сопоставления с логами."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Ядро CRM для туристического бизнеса",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        lifespan=lifespan,
    )

    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-request-id"],
    )

    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
