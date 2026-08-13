"""Модели коммуникаций: комментарии, сообщения, звонки."""

from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import MessageChannel, MessageDirection, pg_enum
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import LongText, LongTextOpt, Str32Opt, Str255Opt, Str512Opt


class Comment(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Внутренний комментарий по сделке. Клиенту не виден."""

    __tablename__ = "comments"

    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    text: Mapped[LongText]


class Message(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Сообщение единой ленты переписки с клиентом.

    Одна таблица на все каналы: разделение по мессенджерам сделало бы невозможной
    хронологическую ленту общения.
    """

    __tablename__ = "messages"

    deal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True
    )
    client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True
    )
    channel: Mapped[MessageChannel] = mapped_column(pg_enum(MessageChannel, "message_channel"))
    direction: Mapped[MessageDirection] = mapped_column(
        pg_enum(MessageDirection, "message_direction")
    )
    body: Mapped[LongTextOpt]
    # Идентификатор во внешней системе: нужен для дедупликации при повторной
    # доставке вебхука и для синхронизации статусов доставки.
    external_message_id: Mapped[Str255Opt] = mapped_column(index=True)


class CallLog(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Запись о звонке с транскрибацией."""

    __tablename__ = "call_logs"

    deal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True
    )
    client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    # Номер хранится маскированным: менеджеру не нужен полный номер для работы,
    # а его копирование — основной канал утечки клиентской базы.
    phone_masked: Mapped[Str32Opt]
    duration_sec: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    recording_url: Mapped[Str512Opt]
    transcript_text: Mapped[LongTextOpt]
    ai_summary: Mapped[LongTextOpt]
