"""Роутер справочника шаблонов документов."""

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError
from app.documents.models import Document
from app.reference.document_templates.models import DocumentTemplate
from app.reference.document_templates.schemas import (
    DocumentTemplateCreate,
    DocumentTemplateFilter,
    DocumentTemplateRead,
    DocumentTemplateUpdate,
)


class DocumentTemplateService(
    CRUDService[DocumentTemplate, DocumentTemplateCreate, DocumentTemplateUpdate]
):
    model = DocumentTemplate
    default_order_by = ("name",)
    unique_fields = (("name", "type"),)
    entity_name = "Шаблон документа"

    async def _check_delete(self, obj: DocumentTemplate) -> None:
        stmt = select(Document.id).where(Document.template_id == obj.id).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError(
                "По шаблону уже сформированы документы. Деактивируйте его вместо удаления"
            )


router = build_crud_router(
    service_class=DocumentTemplateService,
    prefix="/document-templates",
    tags=["Справочники: шаблоны документов"],
    read_schema=DocumentTemplateRead,
    create_schema=DocumentTemplateCreate,
    update_schema=DocumentTemplateUpdate,
    filter_schema=DocumentTemplateFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="document_templates",
)
