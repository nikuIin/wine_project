from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.deal import Deal
from schemas.deal_schema import DealUpdateSchema, LostCreateSchema


class AbstractDealService(ABC):
    @abstractmethod
    async def create(self, deal_create_schema: ...):
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, deal_id: UUID, deal_update_schema: DealUpdateSchema
    ) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        deal_id: UUID,
    ) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def close_deal(self, deal_id: UUID, lost: LostCreateSchema) -> int:
        raise NotImplementedError

    @abstractmethod
    async def change_sale_stage(
        self, deal_id: UUID, sale_stage_id: int
    ) -> int:
        raise NotImplementedError
