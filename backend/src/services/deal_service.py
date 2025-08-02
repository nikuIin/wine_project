from uuid import UUID

from fastapi import Depends

from domain.entities.deal import Deal
from dto.deal_dto import DealCreateDTO, DealUpdateDTO, LostReasonDTO
from repository.abc.deal_repository_abc import AbstractDealRepository
from repository.article_repository import L
from repository.deal_repository import deal_repository_dependency
from schemas.deal_schema import DealUpdateSchema, LostCreateSchema
from services.abc.deal_service_abc import AbstractDealService


class DealService(AbstractDealService):
    def __init__(
        self,
        deal_repository: AbstractDealRepository,
    ):
        self.__deal_repository = deal_repository

    async def create(self, deal_create_schema: ...):
        return await self.__deal_repository.create(
            deal_create=DealCreateDTO(
                **deal_create_schema.model_dump(),
            )
        )

    async def close_deal(
        self, deal_id: UUID, lost: LostCreateSchema | None = None
    ) -> int:
        return await self.__deal_repository.close_deal(
            deal_id=deal_id,
            lost=LostReasonDTO(**lost.model_dump(exclude_unset=True))
            if lost
            else None,
        )

    async def update(
        self, deal_id: UUID, deal_update_schema: DealUpdateSchema
    ) -> Deal | None:
        return await self.__deal_repository.update(
            deal_id=deal_id,
            deal_update=DealUpdateDTO(**deal_update_schema.model_dump()),
        )


def deal_service_dependency(
    deal_repository: AbstractDealRepository = Depends(
        deal_repository_dependency
    ),
) -> AbstractDealService:
    return DealService(deal_repository=deal_repository)
