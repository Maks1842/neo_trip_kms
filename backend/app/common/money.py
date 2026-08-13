"""Работа с денежными суммами.

В базе суммы хранятся целым числом в минимальных единицах валюты (копейках),
в API передаются в основных единицах (рублях) типом Decimal.
Этот модуль — единственное место перевода между двумя представлениями.
"""

from decimal import ROUND_HALF_UP, Decimal

from app.core.exceptions import BusinessValidationError


def to_minor(amount: Decimal, minor_unit: int) -> int:
    """Основные единицы -> минимальные (1234.56 руб. -> 123456 коп.).

    Округление ROUND_HALF_UP, а не банковское: пользователь ожидает, что 0.5 копейки
    округлится вверх, как в бухгалтерских расчётах.
    """
    if minor_unit < 0:
        raise BusinessValidationError("Некорректное число знаков после запятой у валюты")
    quantum = Decimal(1).scaleb(-minor_unit)
    rounded = amount.quantize(quantum, rounding=ROUND_HALF_UP)
    return int(rounded.scaleb(minor_unit))


def to_major(amount_minor: int, minor_unit: int) -> Decimal:
    """Минимальные единицы -> основные (123456 коп. -> 1234.56 руб.)."""
    if minor_unit < 0:
        raise BusinessValidationError("Некорректное число знаков после запятой у валюты")
    return Decimal(amount_minor).scaleb(-minor_unit)
