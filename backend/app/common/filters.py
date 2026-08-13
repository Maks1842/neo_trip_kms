"""Базовый класс фильтров списка.

Фильтр — это Pydantic-модель, которая умеет превращать себя в набор условий SQLAlchemy.
Логика запроса остаётся в фильтре, а сервис и роутер о конкретных полях не знают.
"""

from collections.abc import Sequence

from sqlalchemy import ColumnElement

from app.common.schemas import BaseSchema


class BaseFilter(BaseSchema):
    """Базовый фильтр: по умолчанию не накладывает условий."""

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        """Условия WHERE, соответствующие заполненным полям фильтра."""
        return []
