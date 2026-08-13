"""Типы колонок, переиспользуемые во всех моделях.

Смысл файла: точность денег, процентов и длины строк задаются в одном месте,
а не повторяются в каждой из 28 таблиц.
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from sqlalchemy import BigInteger, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, TIMESTAMP
from sqlalchemy.orm import mapped_column

# ---------- Деньги ----------
# Хранятся целым числом в минимальных единицах валюты (копейках).
# Причина: Decimal в PostgreSQL точен, но при обмене с 1С и эквайрингом суммы всё равно
# приходят в минимальных единицах, а целое число исключает расхождения на округлениях.
# Перевод в рубли выполняется только на границе API (см. app/common/money.py).
Money = Annotated[int, mapped_column(BigInteger)]
MoneyOptional = Annotated[int | None, mapped_column(BigInteger, nullable=True)]

# ---------- Проценты и рейтинги ----------
# Это НЕ деньги: комиссия партнёра и рейтинг отеля остаются дробными.
Percent = Annotated[Decimal, mapped_column(Numeric(5, 2))]
PercentOptional = Annotated[Decimal | None, mapped_column(Numeric(5, 2), nullable=True)]

# ---------- Строки фиксированной длины ----------
Str2 = Annotated[str, mapped_column(String(2))]
Str3 = Annotated[str, mapped_column(String(3))]
Str16 = Annotated[str, mapped_column(String(16))]
Str32 = Annotated[str, mapped_column(String(32))]
Str64 = Annotated[str, mapped_column(String(64))]
Str120 = Annotated[str, mapped_column(String(120))]
Str255 = Annotated[str, mapped_column(String(255))]
Str512 = Annotated[str, mapped_column(String(512))]

Str32Opt = Annotated[str | None, mapped_column(String(32), nullable=True)]
Str64Opt = Annotated[str | None, mapped_column(String(64), nullable=True)]
Str120Opt = Annotated[str | None, mapped_column(String(120), nullable=True)]
Str255Opt = Annotated[str | None, mapped_column(String(255), nullable=True)]
Str512Opt = Annotated[str | None, mapped_column(String(512), nullable=True)]

# ---------- Длинный текст ----------
LongText = Annotated[str, mapped_column(Text)]
LongTextOpt = Annotated[str | None, mapped_column(Text, nullable=True)]

# ---------- JSONB ----------
JSONBDict = Annotated[
    dict[str, Any],
    mapped_column(JSONB, default=dict, server_default=func.jsonb_build_object()),
]

# ---------- Массив строк ----------
StrList = Annotated[
    list[str],
    mapped_column(ARRAY(String(64)), default=list, server_default="{}"),
]

# ---------- Прочее ----------
IPAddressOpt = Annotated[str | None, mapped_column(INET, nullable=True)]
TimestampOpt = Annotated[datetime | None, mapped_column(TIMESTAMP(timezone=True), nullable=True)]
