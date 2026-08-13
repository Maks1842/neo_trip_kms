"""Модели документов и вложений."""

from datetime import datetime
from typing import Final
from uuid import UUID

from sqlalchemy import ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import (
    AttachmentFileType,
    AttachmentSource,
    DocumentStatus,
    DocumentType,
    pg_enum,
)
from app.db.mixins import CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import Str64, Str255Opt, Str512

# Допустимые значения entity_type для полиморфных связей. Внешним ключом такая
# связь не защищена, поэтому список фиксируется здесь и проверяется в схемах —
# иначе в таблице со временем окажутся Deal, deal и deals одновременно.
POLYMORPHIC_ENTITY_TYPES: Final[frozenset[str]] = frozenset(
    {
        "client",
        "deal",
        "deal_item",
        "lead",
        "message",
        "payment",
        "tourist",
        "accommodation",
    }
)


class Document(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Сгенерированный по шаблону документ: договор, счёт или ваучер."""

    __tablename__ = "documents"

    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    template_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_templates.id", ondelete="SET NULL"), nullable=True
    )
    # Тип фиксируется на момент генерации: шаблон потом может измениться.
    type: Mapped[DocumentType] = mapped_column(pg_enum(DocumentType, "document_type"))
    file_url: Mapped[Str512]
    status: Mapped[DocumentStatus] = mapped_column(
        pg_enum(DocumentStatus, "document_status"), default=DocumentStatus.DRAFT
    )
    generated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Attachment(UUIDPkMixin, TimestampMixin, CompanyMixin, Base):
    """Файл, прикреплённый к произвольной сущности.

    Одна полиморфная таблица вместо поля file_url в каждой модели: скан паспорта
    может прийти в сообщении, а относиться к клиенту, и дублировать хранение
    для каждого владельца бессмысленно.
    """

    __tablename__ = "attachments"
    __table_args__ = (Index("ix_attachments_entity", "entity_type", "entity_id"),)

    entity_type: Mapped[Str64]
    entity_id: Mapped[UUID]
    uploaded_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    file_url: Mapped[Str512]
    file_name: Mapped[Str255Opt]
    file_type: Mapped[AttachmentFileType] = mapped_column(
        pg_enum(AttachmentFileType, "attachment_file_type"),
        default=AttachmentFileType.OTHER,
    )
    source: Mapped[AttachmentSource] = mapped_column(
        pg_enum(AttachmentSource, "attachment_source"),
        default=AttachmentSource.MANUAL,
    )
