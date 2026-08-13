"""Справочник шаблонов документов."""

from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import DocumentType, pg_enum
from app.db.mixins import ActiveMixin, CompanyMixin, TimestampMixin, UUIDPkMixin
from app.db.types import LongText, Str255


class DocumentTemplate(UUIDPkMixin, TimestampMixin, CompanyMixin, ActiveMixin, Base):
    """Шаблон договора, счёта или ваучера с плейсхолдерами для подстановки данных сделки."""

    __tablename__ = "document_templates"

    name: Mapped[Str255]
    type: Mapped[DocumentType] = mapped_column(pg_enum(DocumentType, "document_type"), index=True)
    # Отдельная форма под конкретный объект размещения: у части отелей есть
    # собственные требования к бланкам.
    accommodation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accommodations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    template_body: Mapped[LongText]
