"""Роутер справочника этапов воронок."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.common.crud_router import CrudPermissions, build_crud_router
from app.common.service import CRUDService
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.deals.models import Deal
from app.reference.deal_stages.models import DealStage
from app.reference.deal_stages.schemas import (
    DealStageCreate,
    DealStageFilter,
    DealStageRead,
    DealStageUpdate,
    ReorderRequest,
)
from app.users.models import User

PERMISSIONS = CrudPermissions(read="reference.read", write="reference.manage")


class DealStageService(CRUDService[DealStage, DealStageCreate, DealStageUpdate]):
    model = DealStage
    default_order_by = ("sort_order",)
    unique_fields = (("funnel_type", "name"),)
    entity_name = "Этап воронки"

    async def _check_delete(self, obj: DealStage) -> None:
        stmt = select(Deal.id).where(Deal.stage_id == obj.id).limit(1)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Нельзя удалить этап, на котором находятся сделки")

    async def reorder(self, data: ReorderRequest) -> list[DealStage]:
        """Меняет порядок этапов одним пакетом.

        Ограничение уникальности объявлено отложенным, поэтому промежуточные
        совпадения порядковых номеров внутри транзакции допустимы и проверяются
        только при её завершении.
        """
        ids = [item.id for item in data.items]
        stmt = select(DealStage).where(
            DealStage.id.in_(ids),
            DealStage.company_id == self.actor.company_id,
        )
        stages = {stage.id: stage for stage in (await self.session.execute(stmt)).scalars().all()}

        missing = set(ids) - set(stages)
        if missing:
            raise NotFoundError("Часть этапов не найдена")

        funnels = {stages[item.id].funnel_type for item in data.items}
        if len(funnels) > 1:
            raise ConflictError("Переупорядочивать можно только этапы одной воронки")

        for item in data.items:
            stages[item.id].sort_order = item.sort_order
        await self.session.flush()

        # После UPDATE поле updated_at пересчитывается на стороне БД и помечается
        # как устаревшее. Без явного обновления сериализация ответа произошла бы
        # уже после закрытия сессии и упала бы на попытке дочитать атрибут.
        for stage in stages.values():
            await self.session.refresh(stage)

        return sorted(stages.values(), key=lambda stage: stage.sort_order)


router = build_crud_router(
    service_class=DealStageService,
    prefix="/deal-stages",
    tags=["Справочники: этапы воронок"],
    read_schema=DealStageRead,
    create_schema=DealStageCreate,
    update_schema=DealStageUpdate,
    filter_schema=DealStageFilter,
    permissions=PERMISSIONS,
    resource_name="deal_stages",
)

# Маршрут объявлен в отдельном роутере и подключается ДО типового CRUD:
# иначе путь /deal-stages/reorder совпал бы с шаблоном /deal-stages/{item_id}
# и «reorder» попытались бы разобрать как идентификатор.
custom_router = APIRouter(prefix="/deal-stages", tags=["Справочники: этапы воронок"])


@custom_router.patch(
    "/reorder",
    response_model=list[DealStageRead],
    status_code=status.HTTP_200_OK,
    operation_id="deal_stages_reorder",
    summary="Изменение порядка этапов",
)
async def reorder_stages(
    data: ReorderRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(PERMISSIONS.write))],
) -> list[DealStage]:
    return await DealStageService(session, user).reorder(data)
