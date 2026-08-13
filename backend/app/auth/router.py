"""Эндпоинты авторизации."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, client_ip
from app.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    TokenPair,
)
from app.auth.service import AuthService
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Авторизация"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/login", response_model=TokenPair, summary="Вход в систему")
async def login(data: LoginRequest, request: Request, session: DbDep) -> TokenPair:
    return await AuthService(session).login(
        data.email,
        data.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )


@router.post("/refresh", response_model=TokenPair, summary="Обновление пары токенов")
async def refresh(data: RefreshRequest, request: Request, session: DbDep) -> TokenPair:
    return await AuthService(session).refresh(
        data.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
)
async def logout(data: RefreshRequest, session: DbDep) -> None:
    await AuthService(session).logout(data.refresh_token)


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход на всех устройствах",
)
async def logout_all(user: CurrentUser, session: DbDep) -> None:
    await AuthService(session).logout_all(user)


@router.get("/me", response_model=MeResponse, summary="Профиль текущего пользователя")
async def me(user: CurrentUser) -> MeResponse:
    return MeResponse.model_validate(user)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Смена пароля",
)
async def change_password(
    data: ChangePasswordRequest,
    user: CurrentUser,
    session: DbDep,
) -> None:
    await AuthService(session).change_password(user, data.current_password, data.new_password)
