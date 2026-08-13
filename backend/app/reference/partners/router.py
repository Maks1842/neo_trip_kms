"""Роутер справочника партнёров."""

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError
from app.deals.models import Deal
from app.reference.partners.models import Partner
from app.reference.partners.schemas import (
    PartnerCreate,
    PartnerFilter,
    PartnerRead,
    PartnerUpdate,
)


class PartnerService(CRUDService[Partner, PartnerCreate, PartnerUpdate]):
    model = Partner
    default_order_by = ("name",)
    unique_fields = (("name",),)
    entity_name = "Партнёр"

    async def _check_delete(self, obj: Partner) -> None:
        # Партнёр участвует в атрибуции сделок: его удаление обнулило бы историю
        # источников. Вместо удаления партнёра деактивируют.
        stmt = select(Deal.id).where(Deal.partner_id == obj.id).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Партнёр связан со сделками. Деактивируйте его вместо удаления")


router = build_crud_router(
    service_class=PartnerService,
    prefix="/partners",
    tags=["Справочники: партнёры"],
    read_schema=PartnerRead,
    create_schema=PartnerCreate,
    update_schema=PartnerUpdate,
    filter_schema=PartnerFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="partners",
)
