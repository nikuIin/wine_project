from fastapi import Depends

from dto.deal_dto import DealCreateDTO
from repository.abc.deal_repository_abc import AbstractDealRepository
from repository.deal_repository import deal_repository_dependency
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


def deal_service_dependency(
    deal_repository: AbstractDealRepository = Depends(
        deal_repository_dependency
    ),
) -> AbstractDealService:
    return DealService(deal_repository=deal_repository)
