"""Сборка API версии 1."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.auth.router import router as auth_router
from app.reference.router import reference_router
from app.roles.router import router as roles_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(roles_router)
api_router.include_router(reference_router)
