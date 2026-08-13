"""Схемы авторизации."""

from uuid import UUID

from pydantic import EmailStr, Field

from app.common.schemas import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=1)


class RefreshRequest(BaseSchema):
    refresh_token: str = Field(min_length=1)


class TokenPair(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # срок жизни токена доступа в секундах


class ChangePasswordRequest(BaseSchema):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class CompanyBrief(BaseSchema):
    id: UUID
    name: str
    slug: str


class RoleBrief(BaseSchema):
    id: UUID
    name: str
    permissions: list[str]


class MeResponse(BaseSchema):
    """Профиль текущего пользователя.

    Права отдаются сервером, а не вычисляются клиентом из токена: клиент не должен
    самостоятельно разбирать JWT и делать выводы о своих полномочиях.
    """

    id: UUID
    full_name: str
    email: str
    phone: str | None
    is_active: bool
    company: CompanyBrief
    role: RoleBrief
