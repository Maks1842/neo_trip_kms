"""Параметры постраничного вывода."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query

from app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class PageParams:
    """Границы выборки и порядок сортировки."""

    limit: int
    offset: int
    order_by: str | None = None
    desc: bool = False


def page_params(
    limit: Annotated[int | None, Query(ge=1, description="Размер страницы")] = None,
    offset: Annotated[int, Query(ge=0, description="Смещение от начала списка")] = 0,
    order_by: Annotated[str | None, Query(description="Поле сортировки")] = None,
    desc: Annotated[bool, Query(description="Сортировка по убыванию")] = False,
) -> PageParams:
    """Зависимость FastAPI: разбирает параметры пагинации из query-строки."""
    settings = get_settings()
    effective_limit = limit or settings.default_page_size
    # Верхняя граница защищает от запроса всей таблицы одним вызовом.
    effective_limit = min(effective_limit, settings.max_page_size)
    return PageParams(limit=effective_limit, offset=offset, order_by=order_by, desc=desc)


PageDep = Annotated[PageParams, Depends(page_params)]
