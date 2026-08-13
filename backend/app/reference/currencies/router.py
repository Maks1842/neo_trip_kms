"""Роутер справочника валют."""

from sqlalchemy import select

from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError
from app.deals.models import Deal, DealItem
from app.payments.models import Payment
from app.reference.currencies.models import Currency
from app.reference.currencies.schemas import (
    CurrencyCreate,
    CurrencyFilter,
    CurrencyRead,
    CurrencyUpdate,
)
from app.reference.tariff_entries.models import TariffEntry


class CurrencyService(CRUDService[Currency, CurrencyCreate, CurrencyUpdate]):
    model = Currency
    tenant_scoped = False
    default_order_by = ("code",)
    unique_fields = (("code",),)
    entity_name = "Валюта"

    async def _check_delete(self, obj: Currency) -> None:
        # Валюта участвует в расчётах: её удаление сломало бы пересчёт уже
        # сохранённых сумм из минимальных единиц в основные.
        for model, title in (
            (TariffEntry, "тарифах"),
            (Deal, "сделках"),
            (DealItem, "позициях сделок"),
            (Payment, "платежах"),
        ):
            stmt = select(model.id).where(model.currency_id == obj.id).limit(1)
            if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
                raise ConflictError(f"Валюта используется в {title} и не может быть удалена")


router = build_crud_router(
    service_class=CurrencyService,
    prefix="/currencies",
    tags=["Справочники: валюты"],
    read_schema=CurrencyRead,
    create_schema=CurrencyCreate,
    update_schema=CurrencyUpdate,
    filter_schema=CurrencyFilter,
    permissions=CrudPermissions(read="reference.read", write="reference.manage"),
    resource_name="currencies",
)
