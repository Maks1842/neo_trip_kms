"""Модели клиента и его контактов."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, false, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import ClientContactType, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import (
    JSONBDict,
    Str32Opt,
    Str64Opt,
    Str120Opt,
    Str255,
    Str255Opt,
    StrList,
    TimestampOpt,
)

if TYPE_CHECKING:
    from app.leads.models import Lead


class Client(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Сквозная карточка клиента — очищенный профиль поверх сырых заявок."""

    __tablename__ = "clients"

    full_name: Mapped[Str255]
    birth_date: Mapped[date | None] = mapped_column(nullable=True)

    # Текущие паспортные данные. В сделке хранится их слепок на момент оформления,
    # поэтому изменение этих полей не переписывает историю.
    passport_series: Mapped[Str32Opt]
    passport_number: Mapped[Str32Opt]
    passport_issued_by: Mapped[Str255Opt]
    passport_issued_date: Mapped[date | None] = mapped_column(nullable=True)
    citizenship: Mapped[Str64Opt]

    # Бытовые предпочтения: аллергии, привычки, состав семьи.
    preferences: Mapped[JSONBDict]
    # Данные о здоровье — специальная категория персональных данных, их обработка
    # требует отдельного согласия. Здесь хранится только факт и дата согласия,
    # сами данные в этой таблице не лежат.
    health_data_consented_at: Mapped[TimestampOpt]
    tags: Mapped[StrList]

    source_lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL", use_alter=True, name="fk_clients_source_lead"),
        nullable=True,
    )

    source_lead: Mapped["Lead | None"] = relationship(
        foreign_keys=[source_lead_id],
        lazy="raise",
        post_update=True,
    )
    contacts: Mapped[list["ClientContact"]] = relationship(
        back_populates="client",
        lazy="raise",
        cascade="all, delete-orphan",
    )


class ClientContact(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Контакт клиента: телефон, почта или мессенджер.

    Вынесен в отдельную таблицу, а не в JSONB: нужен обратный поиск клиента по номеру
    при входящем звонке, ограничение уникальности против дублей карточек и защита
    основного контакта от правки.
    """

    __tablename__ = "client_contacts"
    __table_args__ = (
        # Один и тот же контакт не может принадлежать двум карточкам — основная
        # защита от размножения дублей клиента.
        UniqueConstraint("type", "value", name="uq_client_contacts_type_value"),
        # Ровно один основной контакт на клиента. Частичный индекс — единственный
        # способ выразить это ограничение, обычным UniqueConstraint не описывается.
        Index(
            "uq_client_contacts_primary",
            "client_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )

    client_id: Mapped[UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[ClientContactType] = mapped_column(
        pg_enum(ClientContactType, "client_contact_type")
    )
    value: Mapped[Str255]
    is_primary: Mapped[bool] = mapped_column(default=False, server_default=false(), nullable=False)
    # Защита основного контакта от изменения менеджером: снижает риск увода клиента.
    is_readonly: Mapped[bool] = mapped_column(default=False, server_default=false(), nullable=False)
    verified_at: Mapped[TimestampOpt]
    label: Mapped[Str120Opt]

    client: Mapped["Client"] = relationship(back_populates="contacts", lazy="raise")
