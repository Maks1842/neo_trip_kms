"""Обработчики исключений: единый формат тела ошибки на весь API.

Любая ошибка — доменная, валидации, HTTP или необработанная — возвращается клиенту
в одной и той же структуре, чтобы фронтенд разбирал её единственной функцией.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def _error_body(
    code: str,
    message: str,
    request: Request,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": getattr(request.state, "request_id", None),
        }
    }


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Доменные исключения приложения."""
    assert isinstance(exc, AppError)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, request, exc.details),
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ошибки валидации Pydantic — приводим к тому же формату, что и остальные."""
    assert isinstance(exc, RequestValidationError)
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]) or None,
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_error_body("validation_error", "Данные не прошли проверку", request, details),
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """HTTPException из FastAPI/Starlette (в том числе 404 на несуществующий маршрут)."""
    assert isinstance(exc, StarletteHTTPException)
    code_by_status = {
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
    }
    code = code_by_status.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(code, str(exc.detail), request),
        headers=getattr(exc, "headers", None),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Необработанное исключение.

    В продакшене наружу уходит только код ошибки и request_id — по нему инцидент
    находится в логах. Traceback клиенту не показывается.
    """
    settings = get_settings()
    logger.exception(
        "Необработанное исключение при обработке запроса %s %s", request.method, request.url.path
    )
    message = (
        "Внутренняя ошибка сервера" if settings.is_production else f"{type(exc).__name__}: {exc}"
    )
    return JSONResponse(
        status_code=500,
        content=_error_body("internal_error", message, request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Подключает все обработчики к приложению."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
