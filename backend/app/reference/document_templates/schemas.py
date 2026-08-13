"""Схемы справочника шаблонов документов."""

from collections.abc import Sequence
from uuid import UUID

from pydantic import Field
from sqlalchemy import ColumnElement

from app.common.filters import BaseFilter
from app.common.schemas import BaseSchema, IdSchema, TimestampSchema
from app.db.enums import DocumentType
from app.reference.document_templates.models import DocumentTemplate


class DocumentTemplateCreate(BaseSchema):
    name: str = Field(max_length=255)
    type: DocumentType
    accommodation_id: UUID | None = None
    template_body: str = Field(min_length=1)
    is_active: bool = True


class DocumentTemplateUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    type: DocumentType | None = None
    accommodation_id: UUID | None = None
    template_body: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class DocumentTemplateRead(IdSchema, TimestampSchema):
    name: str
    type: DocumentType
    accommodation_id: UUID | None
    template_body: str
    is_active: bool


class DocumentTemplateFilter(BaseFilter):
    type: DocumentType | None = None
    accommodation_id: UUID | None = None
    search: str | None = None
    is_active: bool | None = None

    def conditions(self) -> Sequence[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if self.type is not None:
            conditions.append(DocumentTemplate.type == self.type)
        if self.accommodation_id is not None:
            conditions.append(DocumentTemplate.accommodation_id == self.accommodation_id)
        if self.search:
            conditions.append(DocumentTemplate.name.ilike(f"%{self.search}%"))
        if self.is_active is not None:
            conditions.append(DocumentTemplate.is_active.is_(self.is_active))
        return conditions
