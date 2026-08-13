"""Проверки перевода денежных сумм между представлениями."""

from decimal import Decimal

import pytest

from app.common.ids import uuid7
from app.common.money import to_major, to_minor


@pytest.mark.parametrize(
    ("value", "minor_unit", "expected"),
    [
        (Decimal("1234.56"), 2, 123456),
        (Decimal("0.01"), 2, 1),
        (Decimal("0"), 2, 0),
        (Decimal("1000"), 2, 100000),
        (Decimal("1500"), 0, 1500),  # валюта без дробной части
        (Decimal("99.999"), 2, 10000),  # округление половин вверх
        (Decimal("1.005"), 2, 101),
    ],
)
def test_to_minor(value: Decimal, minor_unit: int, expected: int) -> None:
    assert to_minor(value, minor_unit) == expected


@pytest.mark.parametrize(
    ("value", "minor_unit", "expected"),
    [
        (123456, 2, Decimal("1234.56")),
        (1, 2, Decimal("0.01")),
        (1500, 0, Decimal("1500")),
    ],
)
def test_to_major(value: int, minor_unit: int, expected: Decimal) -> None:
    assert to_major(value, minor_unit) == expected


def test_round_trip_is_lossless() -> None:
    """Сумма, прошедшая оба преобразования, не должна измениться."""
    for raw in ("0.01", "10.00", "999999.99", "1234.56"):
        amount = Decimal(raw)
        assert to_major(to_minor(amount, 2), 2) == amount


def test_uuid7_version_and_monotonicity() -> None:
    first = uuid7()
    second = uuid7()
    assert first.version == 7
    # Метка времени в старших битах делает идентификаторы возрастающими,
    # что и обеспечивает локальность вставки в индекс.
    assert second > first
