"""Модель сырой заявки (лида)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import LeadStatus, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import JSONBDict, LongTextOpt, Str32Opt, Str120Opt, Str255Opt

if TYPE_CHECKING:
    from app.clients.models import Client


class Lead(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Заявка в том виде, в каком её оставил клиент.

    Поля raw_* сознательно не нормализуются: исходный текст обращения нужен для
    разбора спорных случаев и обучения парсеров. Очищенные данные живут в Client.
    """

    __tablename__ = "leads"

    source: Mapped[Str120Opt]
    raw_full_name: Mapped[Str255Opt]
    raw_phone: Mapped[Str32Opt]
    raw_email: Mapped[Str255Opt]
    raw_message: Mapped[LongTextOpt]
    # Произвольные поля лендинговой формы: позволяет подключить новый источник
    # заявок без миграции схемы.
    form_data: Mapped[JSONBDict]
    status: Mapped[LeadStatus] = mapped_column(
        pg_enum(LeadStatus, "lead_status"),
        default=LeadStatus.NEW,
        index=True,
    )

    # Взаимная ссылка с clients: FK создаётся отдельной командой ALTER TABLE,
    # иначе таблицы невозможно создать — каждая ссылается на другую.
    converted_client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "clients.id", ondelete="SET NULL", use_alter=True, name="fk_leads_converted_client"
        ),
        nullable=True,
    )
    # Ссылка на канонический лид, если текущий признан дублем: по ней собирается
    # группа связанных обращений одного человека.
    duplicate_of_lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
    )

    converted_client: Mapped["Client | None"] = relationship(
        foreign_keys=[converted_client_id],
        lazy="raise",
        post_update=True,
    )
