"""Проверка работоспособности сервиса."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["Служебные"])


@router.get("", summary="Состояние сервиса")
async def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }


@router.get("/db", summary="Состояние подключения к базе данных")
async def health_db(session: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, Any]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
